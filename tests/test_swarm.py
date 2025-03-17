"""Test suite for SugarSwarm class."""

import io
import sys

from unittest import mock

import pytest
import sh

from sugar.extensions.swarm import SugarSwarm
from sugar.logs import SugarError, SugarLogs


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
        with pytest.raises(SystemExit):
            sugar_swarm._get_services_names(all=True)

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
        with pytest.raises(SystemExit):
            sugar_swarm._get_nodes_names(all=True)

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
        with pytest.raises(SystemExit):
            sugar_swarm._cmd_deploy()

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

    def test_cmd_inspect_multiple_services(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test _cmd_inspect sets correct parameters."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with pytest.raises(SystemExit):
                sugar_swarm._cmd_inspect(service='svc1,svc2')

    def test_cmd_inspect_single_service(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_inspect sets correct parameters for a single service."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm, '_call_backend_app'
            ) as mock_call:
                sugar_swarm._cmd_inspect(service='svc1')
                mock_call.assert_called_once_with(
                    'inspect', services=['svc1'], options_args=[]
                )

    def test_cmd_inspect_service_without_stack_message(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test raises correct error, service is provided without stack."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
                sugar_swarm._cmd_inspect(service='my-service', stack='')
                mock_error.assert_called_once_with(
                    """Both service name and stack name must be
              provided together for inspect""",
                    SugarError.SUGAR_INVALID_PARAMETER,
                )

    def test_cmd_inspect_service_without_service_message(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test raises correct error, service is provided without stack."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch('sugar.logs.SugarLogs.raise_error') as mock_error:
                sugar_swarm._cmd_inspect(service='', stack='svc1')
                mock_error.assert_called_once_with(
                    """Both service name and stack name must be
              provided together for inspect""",
                    SugarError.SUGAR_INVALID_PARAMETER,
                )

    def test_cmd_logs(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_logs formats options correctly."""
        with mock.patch.object(
            sugar_swarm, '_get_services_names', return_value=['svc1']
        ):
            with mock.patch.object(
                sugar_swarm, '_get_list_args', return_value=[]
            ):
                with mock.patch.object(
                    sugar_swarm, '_call_service_command'
                ) as mock_call:
                    sugar_swarm._cmd_logs(
                        services='svc1',
                        details=True,
                        follow=True,
                        since='2h',
                        tail='100',
                    )
                    mock_call.assert_called_once_with(
                        'logs',
                        services=['svc1'],
                        options_args=[
                            '--details',
                            '--follow',
                            '--since',
                            '2h',
                            '--tail',
                            '100',
                        ],
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
        with pytest.raises(SystemExit):
            sugar_swarm._cmd_ps()

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

    def test_perform_service_rollback_success(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test _perform_service_rollback returns True on success."""
        sugar_swarm.backend_app.return_value = None
        result = sugar_swarm._perform_service_rollback('svc1', [])
        assert result is True

    def test_perform_service_rollback_no_previous_spec(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test  returns False when no previous spec."""
        error_output = io.StringIO(
            'service svc1 does not have a previous spec'
        )
        print('error_output :', error_output)
        sugar_swarm.backend_app.return_value = None
        sugar_swarm.backend_app.side_effect = (
            lambda *args, _err=None, **kwargs: _err.write(
                'service svc1 does not have a previous spec'
            )
            if _err is not None
            else None
        )

        with mock.patch.object(SugarLogs, 'print_warning') as mock_warning:
            result = sugar_swarm._perform_service_rollback('svc1', [])
            assert result is False
            mock_warning.assert_called_once()

    def test_get_services_to_rollback_with_stack_and_all(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test _get_services_to_rollback with stack and all=True."""
        with mock.patch.object(
            sugar_swarm,
            '_get_services_from_stack',
            return_value=['stack_svc1', 'stack_svc2'],
        ):
            result = sugar_swarm._get_services_to_rollback('', True, 'stack')
            assert result == ['stack_svc1', 'stack_svc2']

    def test_get_services_to_rollback_with_stack_and_services(
        self, sugar_swarm: SugarSwarm
    ) -> None:
        """Test _get_services_to_rollback with stack and services."""
        result = sugar_swarm._get_services_to_rollback(
            'svc1,svc2', False, 'stack'
        )
        assert result == ['stack_svc1', 'stack_svc2']

    def test_cmd_rollback(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_rollback performs rollbacks and reports results."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm,
                '_get_services_to_rollback',
                return_value=['svc1', 'svc2'],
            ):
                with mock.patch.object(
                    sugar_swarm,
                    '_perform_service_rollback',
                    side_effect=[True, False],
                ) as mock_rollback:
                    with mock.patch('builtins.print') as mock_print:
                        sugar_swarm._cmd_rollback(services='svc1,svc2')
                        ROLLBACK_CALL_COUNT = 2
                        assert mock_rollback.call_count == ROLLBACK_CALL_COUNT
                        # Use assert_called_once to verify the print was called
                        mock_print.assert_called_once()
                        # Check individual components of the message
                        call_args = mock_print.call_args[0][0]
                        assert 'Rollback complete' in call_args
                        assert 'succeeded' in call_args
                        assert 'failed' in call_args
                        # Verify the counts are correct
                        assert '1' in call_args

    def test_cmd_scale_missing_stack(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_scale raises error when stack name is missing."""
        with pytest.raises(SystemExit):
            sugar_swarm._cmd_scale()

    def test_cmd_scale_missing_replicas(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_scale raises error when replicas is missing."""
        with pytest.raises(SystemExit):
            sugar_swarm._cmd_scale(stack='test-stack')

    def test_cmd_scale(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_scale formats arguments correctly."""
        with mock.patch.object(sugar_swarm, '_get_list_args', return_value=[]):
            with mock.patch.object(
                sugar_swarm, '_call_service_command'
            ) as mock_call:
                sugar_swarm._cmd_scale(
                    stack='test', replicas='svc1=3,svc2=5', detach=True
                )
                mock_call.assert_called_once_with(
                    'scale',
                    services=['test_svc1=3', 'test_svc2=5'],
                    options_args=['--detach'],
                )

    @pytest.mark.skip(
        reason='This test is experimental, need to add '
        'more test cases and more integrations to the  cli'
    )
    def test_cmd_update(self, sugar_swarm: SugarSwarm) -> None:
        """Test _cmd_update formats options correctly."""
        with mock.patch.object(
            sugar_swarm, '_get_services_names', return_value=['svc1']
        ):
            with mock.patch.object(
                sugar_swarm, '_get_list_args', return_value=[]
            ):
                with mock.patch.object(
                    sugar_swarm, '_call_service_command'
                ) as mock_call:
                    sugar_swarm._cmd_update(
                        services='svc1',
                        image='nginx:latest',
                        replicas='3',
                        force=True,
                        detach=True,
                        env_add='DEBUG=1,LOG_LEVEL=info',
                    )
                    mock_call.assert_called_once_with(
                        'update',
                        services=['svc1'],
                        options_args=[
                            '--detach',
                            '--force',
                            '--image',
                            'nginx:latest',
                            '--replicas',
                            '3',
                            '--env-add',
                            'DEBUG=1',
                            '--env-add',
                            'LOG_LEVEL=info',
                        ],
                    )

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
