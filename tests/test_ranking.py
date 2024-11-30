from unittest.mock import Mock
import pytest


@pytest.mark.asyncio
async def test_master_ranking(mocker, client, master_ranking_data):
    mocker.patch("sf6_ranking.client.httpx.AsyncClient.get", return_value=Mock(json=lambda: master_ranking_data))

    await client.master_ranking()
    assert master_ranking_data.get("fighter_banner_info") is None
