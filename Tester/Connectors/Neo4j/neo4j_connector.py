import pytest
from unittest.mock import patch, MagicMock

from Backend.Connectors.Neo4j.neo4j_connector import Neo4jConnector

@patch("Backend.Connectors.Neo4j.neo4j_connector.GraphDatabase.driver")
def test_neo4j_connector_init(mock_driver):
    credentials = {
        "url": "bolt://localhost:7687",
        "username": "neo4j",
        "password": "password"
    }

    connector = Neo4jConnector(credentials)

    mock_driver.assert_called_once_with(
        credentials["url"],
        auth=(credentials["username"], credentials["password"])
    )
    assert connector.driver == mock_driver.return_value


@patch("Backend.Connectors.Neo4j.neo4j_connector.GraphDatabase.driver")
def test_neo4j_connect_test(mock_driver):
    mock_driver_instance = MagicMock()
    mock_driver.return_value = mock_driver_instance

    # Context manager support
    mock_driver_instance.__enter__.return_value = mock_driver_instance
    mock_driver_instance.__exit__.return_value = None

    connector = Neo4jConnector({
        "url": "bolt://localhost:7687",
        "username": "neo4j",
        "password": "password"
    })

    driver, message = connector.neo4j_connect_test()

    mock_driver_instance.verify_connectivity.assert_called_once()
    assert driver == mock_driver_instance
    assert message == "Connected to Neo4j"

@patch("Backend.Connectors.Neo4j.neo4j_connector.GraphDatabase.driver")
def test_neo4j_disconnect(mock_driver):
    mock_driver_instance = MagicMock()
    mock_driver.return_value = mock_driver_instance

    mock_driver_instance.__enter__.return_value = mock_driver_instance
    mock_driver_instance.__exit__.return_value = None

    connector = Neo4jConnector({
        "url": "bolt://localhost:7687",
        "username": "neo4j",
        "password": "password"
    })

    connector.neo4j_disconnect()

    mock_driver_instance.close.assert_called_once()

@patch("Backend.Connectors.Neo4j.neo4j_connector.GraphDatabase.driver")
def test_neo4j_delete_nodes_and_relationships(mock_driver):
    mock_driver_instance = MagicMock()
    mock_session = MagicMock()

    mock_driver.return_value = mock_driver_instance
    mock_driver_instance.session.return_value.__enter__.return_value = mock_session
    mock_driver_instance.session.return_value.__exit__.return_value = None

    connector = Neo4jConnector({
        "url": "bolt://localhost:7687",
        "username": "neo4j",
        "password": "password"
    })

    connector.neo4j_delete_nodes_and_relationships()

    mock_session.run.assert_called_once_with(
        "MATCH (n) DETACH DELETE n"
    )
