import pytest
from Projeto_xirico.use_cases.operator_use_cases.list_operator_maneged_orders import ListOperatorMenagedOrders
from Projeto_xirico.use_cases.operator_use_cases.list_operator_shipments import ListOperatorShipments


@pytest.fixture
def list_operator_maneged_orders(mock_repo):
    return ListOperatorMenagedOrders(mock_repo)

@pytest.fixture
def list_operator_shipments(mock_repo):
    return ListOperatorShipments(mock_repo)


def test_list_operator_maneged_orders(mock_repo, list_operator_maneged_orders):
    id=1
    list_operator_maneged_orders.execute(id)
    mock_repo.get_order_gid.assert_called_once()


def test_list_operator_shipmetns(mock_repo, list_operator_shipments):
    id=1
    list_operator_shipments.execute(operator_id= id)

    mock_repo.get_shipment_gid.assert_called_once()
    