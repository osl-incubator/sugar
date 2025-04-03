"""Test suite for SugarSwarm class."""

import io
import sys

from unittest import mock

import pytest
import sh

from sugar.extensions.swarm import SugarSwarm
from sugar.logs import SugarLogs


@pytest.fixture
def sugar_swarm() -> SugarSwarm:
    """Create a SugarSwarm instance for testing."""
    swarm = SugarSwarm()
    swarm.profile_selected = 'test-profile'
    swarm.file = 'test-file.yml'
    swarm.dry_run = False
    swarm.verbose = False
    # Mock backend app and methods
    swarm.backend_app = mock.Mock()
    # Use proper type annotation for the mock
    swarm._call_backend_app = mock.Mock()  # type: ignore
    return swarm


@pytest.fixture
def mock_backend_app(monkeypatch: pytest.MonkeyPatch) -> mock.Mock:
    """Mock sh.docker for all tests."""
    mock_docker = mock.Mock()
    monkeypatch.setattr(sh, 'docker', mock_docker)
    return mock_docker


class TestSugarSwarm:
    """Test suite for SugarSwarm class."""

    def test_load_backend_app(
        self, sugar_swarm: SugarSwarm, mock_backend_app: mock.Mock
    ) -> None:
        """Test _load_backend_app sets correct backend."""
        sugar_swarm._load_backend_app()
        assert sugar_swarm.backend_app == mock_backend_app
        assert sugar_swarm.backend_args == []

    def test_load_backend_args(self, sugar_swarm: SugarSwarm) -> None:
        """Test _load_backend_args properly initializes backend args."""
        sugar_swarm._load_backend_args()
        assert sugar_swarm.backend_args == []

    def test_get_services_names_empty(self, sugar_swarm: SugarSwarm) -> None:
        """Test  returns empty list when no services specified."""
        result = sugar_swarm._get_services_names()
        print('result :', result)
        assert result == []

    def test_get_services_names_with_services(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test  properly parses comma-separated services."""
        result = sugar_swarm._get_services_names(services='svc1,svc2,svc3')
        print('result :', result)
        assert result == ['svc1', 'svc2', 'svc3']

    def test_get_services_names_with_single_service(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test  properly parses comma-separated services."""
        result = sugar_swarm._get_services_names(services='svc1')
        print('result :', result)
        assert result == ['svc1']

    def test_get_services_names_no_services_with_all(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test  raises error when all=True but no services."""
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm._get_services_names(all=True)
            mock_error.assert_called_once()

    def test_get_nodes_names_empty(self, sugar_swarm: SugarSwarm) -> None:
        """Test _get_nodes_names returns empty list when no nodes specified."""
        result = sugar_swarm._get_nodes_names()
        assert result == []

    def test_get_nodes_names_with_nodes(self, sugar_swarm: SugarSwarm) -> None:
        """Test _get_nodes_names properly parses comma-separated nodes."""
        result = sugar_swarm._get_nodes_names(nodes='node1,node2,node3')
        assert result == ['node1', 'node2', 'node3']

    def test_get_nodes_names_no_nodes_with_all(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test _get_nodes_names raises error when all=True but no nodes."""
        # with pytest.raises(SystemExit):
        #     sugar_swarm._get_nodes_names(all=True)
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            sugar_swarm._get_nodes_names(all=True)
            mock_error.assert_called_once()

    def test_call_swarm_command(self, sugar_swarm: SugarSwarm) -> None:
        """Test _call_swarm_command properly sets backend_args."""
        with mock.patch.object(sugar_swarm, '_call_backend_app') as mock_call:
            sugar_swarm._call_swarm_command(
                'init', options_args=['--advertise-addr', '192.168.1.1']
            )
            mock_call.assert_called_once_with(
                'init',
                services=[],
                options_args=['--advertise-addr', '192.168.1.1'],
                cmd_args=[],
                _out=sys.stdout,
                _err=sys.stderr,
            )
        assert sugar_swarm.backend_args == ['swarm']

    def test_call_service_command(self, sugar_swarm: SugarSwarm) -> None:
        """Test _call_service_command properly sets backend_args."""
        with mock.patch.object(sugar_swarm, '_call_backend_app') as mock_call:
            sugar_swarm._call_service_command(
                'ls', options_args=['--filter', 'name=test']
            )
            mock_call.assert_called_once_with(
                'ls',
                services=[],
                options_args=['--filter', 'name=test'],
                cmd_args=[],
                _out=sys.stdout,
                _err=sys.stderr,
            )
        assert sugar_swarm.backend_args == ['service']

    def test_call_node_command(self, sugar_swarm: SugarSwarm) -> None:
        """Test _call_node_command properly sets backend_args."""
        with mock.patch.object(sugar_swarm, '_call_backend_app') as mock_call:
            sugar_swarm._call_node_command(
                'ls',
                nodes=['node1'],
                options_args=['--filter', 'role=manager'],
            )
            mock_call.assert_called_once_with(
                'ls',
                services=['node1'],  # Reuses services parameter for nodes
                options_args=['--filter', 'role=manager'],
                cmd_args=[],
                _out=sys.stdout,
                _err=sys.stderr,
            )
        assert sugar_swarm.backend_args == ['node']

    def test_call_stack_command(self, sugar_swarm: SugarSwarm) -> None:
        """Test _call_stack_command properly sets backend_args."""
        with mock.patch.object(sugar_swarm, '_call_backend_app') as mock_call:
            sugar_swarm._call_stack_command(
                stack_name='test-stack',
                compose_file='docker-compose.yml',
                options_args=['--with-registry-auth'],
                backend_args=['stack', 'deploy', '-c'],
                compose_file_required=True,
            )
            mock_call.assert_called_once_with(
                'test-stack',
                options_args=['--with-registry-auth'],
                _out=sys.stdout,
                _err=sys.stderr,
            )
            assert sugar_swarm.backend_args == [
                'stack',
                'deploy',
                '-c',
                'docker-compose.yml',
            ]

    def test_cmd_init(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_init calls _call_swarm_command properly."""
        with mock.patch.object(
            sugar_swarm,
            '_get_list_args',
            return_value=['--advertise-addr', '192.168.1.1'],
        ):
            with mock.patch.object(
                sugar_swarm, '_call_swarm_command'
            ) as mock_call:
                sugar_swarm._cmd_init(options='--advertise-addr 192.168.1.1')
                mock_call.assert_called_once_with(
                    'init', options_args=['--advertise-addr', '192.168.1.1']
                )

    def test_cmd_join(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_join calls _call_swarm_command properly."""
        with mock.patch.object(
            sugar_swarm, '_get_list_args', return_value=['--token', 'token123']
        ):
            with mock.patch.object(
                sugar_swarm, '_call_swarm_command'
            ) as mock_call:
                sugar_swarm._cmd_join(options='--token token123')
                mock_call.assert_called_once_with(
                    'join', options_args=['--token', 'token123']
                )

    def test_cmd_deploy_missing_stack(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_deploy raises error when stack name is missing."""
        # with pytest.raises(FileNotFoundError):
        #     sugar_swarm._cmd_deploy()
        with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
            with pytest.raises(FileNotFoundError):
                sugar_swarm._cmd_deploy()
            mock_error.assert_called_once()

    @mock.patch('sugar.extensions.base.SugarBase.load')
    def test_cmd_deploy_with_file(
        self, mock_load: mock.Mock, sugar_swarm: SugarSwarm
    ) -> None:
        """Test _cmd_deploy with file parameter."""
        with mock.patch.object(
            sugar_swarm, '_call_stack_command'
        ) as mock_call:
            with mock.patch.object(
                sugar_swarm, '_get_list_args', return_value=[]
            ):
                sugar_swarm._cmd_deploy(
                    stack='test-stack', file='docker-compose.yml'
                )
                mock_call.assert_called_once_with(
                    stack_name='test-stack',
                    compose_file='docker-compose.yml',
                    options_args=[],
                    compose_file_required=True,
                    backend_args=['stack', 'deploy', '-c'],
                )

    def test_cmd_ls_without_stack(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_ls without stack parameter calls service ls."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm, '_call_service_command'
            ) as mock_call:
                sugar_swarm._cmd_ls()
                mock_call.assert_called_once_with('ls', options_args=[])

    def test_cmd_ls_with_stack(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_ls with stack parameter calls stack services."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm, '_call_stack_command'
            ) as mock_call:
                sugar_swarm._cmd_ls(stack='test-stack')
                mock_call.assert_called_once_with(
                    stack_name='test-stack',
                    options_args=[],
                    backend_args=['stack', 'services'],
                    compose_file_required=False,
                )

    def test_cmd_ps_missing_stack(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_ps raises error when stack name is missing."""
        with mock.patch(
            'sugar.logs.SugarLogs.raise_error', side_effect=SystemExit
        ) as mock_error:
            with pytest.raises(SystemExit):
                sugar_swarm._cmd_ps()
            mock_error.assert_called_once()

    def test_cmd_ps_with_stack(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_ps with stack parameter."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm, '_call_stack_command'
            ) as mock_call:
                sugar_swarm._cmd_ps(stack='test-stack')
                mock_call.assert_called_once_with(
                    stack_name='test-stack',
                    options_args=[],
                    compose_file_required=False,
                    backend_args=['stack', 'ps'],
                )

    def test_cmd_ps_with_quiet(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_ps with quiet flag."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm, '_call_stack_command'
            ) as mock_call:
                sugar_swarm._cmd_ps(stack='test-stack', quiet=True)
                mock_call.assert_called_once_with(
                    stack_name='test-stack',
                    options_args=[],
                    compose_file_required=False,
                    backend_args=['stack', 'ps', '--quiet'],
                )

    def test_cmd_rm(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_rm calls _call_stack_command properly."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm, '_call_stack_command'
            ) as mock_call:
                sugar_swarm._cmd_rm(stack='test-stack')
                mock_call.assert_called_once_with(
                    stack_name='test-stack',
                    options_args=[],
                    compose_file_required=False,
                    backend_args=['stack', 'rm'],
                )

    def test_get_services_from_stack(self, sugar_swarm: SugarSwarm) -> None:
        """Test _get_services_from_stack parses output correctly."""
        mock_output = io.StringIO('service1\nservice2\nservice3')
        print('mock_output :', mock_output)
        sugar_swarm.backend_app.return_value = None
        sugar_swarm.backend_app.side_effect = (
            lambda *args, _out=None, **kwargs: _out.write(
                'service1\nservice2\nservice3'
            )
            if _out is not None
            else None
        )

        result = sugar_swarm._get_services_from_stack('test-stack')
        assert result == ['service1', 'service2', 'service3']

    def test_cmd_node(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_node calls appropriate subcommand."""
        with mock.patch.object(sugar_swarm, '_subcmd_node_ls') as mock_ls:
            sugar_swarm._cmd_node(ls=True, options='--filter role=manager')
            mock_ls.assert_called_once_with(options='--filter role=manager')

    def test_subcmd_node_demote(self, sugar_swarm: SugarSwarm) -> None:
        """Test _subcmd_node_demote calls _call_node_command properly."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm, '_call_node_command'
            ) as mock_call:
                sugar_swarm._subcmd_node_demote(nodes='node1,node2')
                mock_call.assert_called_once_with(
                    'demote', nodes=['node1', 'node2'], options_args=[]
                )

    def test_subcmd_node_inspect(self, sugar_swarm: SugarSwarm) -> None:
        """Test _subcmd_node_inspect calls _call_node_command properly."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm, '_call_node_command'
            ) as mock_call:
                sugar_swarm._subcmd_node_inspect(nodes='node1')
                mock_call.assert_called_once_with(
                    'inspect', nodes=['node1'], options_args=[]
                )

    def test_subcmd_node_ls(self, sugar_swarm: SugarSwarm) -> None:
        """Test _subcmd_node_ls calls _call_node_command properly."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm, '_call_node_command'
            ) as mock_call:
                sugar_swarm._subcmd_node_ls()
                mock_call.assert_called_once_with('ls', options_args=[])

    def test_print_node_warning(self, sugar_swarm: SugarSwarm) -> None:
        """Test _print_node_warning calls SugarLogs.print_warning."""
        with mock.patch.object(SugarLogs, 'print_warning') as mock_warning:
            sugar_swarm._print_node_warning()
            mock_warning.assert_called_once()
