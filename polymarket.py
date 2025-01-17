import json

import httpx

from Models import Market
from Models.Market import ClobReward, PolymarketEvent, Tag


class GammaMarketClient:
    def __init__(self):
        self.gamma_url = "https://gamma-api.polymarket.com"
        self.gamma_markets_endpoint = self.gamma_url + "/markets"
        self.gamma_events_endpoint = self.gamma_url + "/events"

    def get_markets(
        self, querystring_params={}, parse_pydantic=False, local_file_path=None) -> "list[Market]":
        if parse_pydantic and local_file_path is not None:
            raise Exception(
                'Cannot use "parse_pydantic" and "local_file" params simultaneously.'
            )

        response = httpx.get(self.gamma_markets_endpoint, params=querystring_params)
        if response.status_code == 200:
            data = response.json()
            if local_file_path is not None:
                with open(local_file_path, "w+") as out_file:
                    json.dump(data, out_file)
            elif not parse_pydantic:
                return data
            else:
                markets: list[Market] = []
                for market_object in data:
                    markets.append(self.__parse_pydantic_market(market_object))
                return markets
        else:
            print(f"Error response returned from api: HTTP {response.status_code}")
            raise Exception()

    @staticmethod
    def __parse_pydantic_market(market_object: dict) -> Market:
        try:
            if "clobRewards" in market_object:
                clob_rewards: list[ClobReward] = []
                for clob_rewards_obj in market_object["clobRewards"]:
                    clob_rewards.append(ClobReward(**clob_rewards_obj))
                market_object["clobRewards"] = clob_rewards

            if "events" in market_object:
                events: list[PolymarketEvent] = []
                for market_event_obj in market_object["events"]:
                    events.append(GammaMarketClient.__parse_nested_event(market_event_obj))
                market_object["events"] = events

            # These two fields below are returned as stringified lists from the api
            if "outcomePrices" in market_object:
                market_object["outcomePrices"] = json.loads(
                    market_object["outcomePrices"]
                )
            if "clobTokenIds" in market_object:
                market_object["clobTokenIds"] = json.loads(
                    market_object["clobTokenIds"]
                )

            return Market(**market_object)
        except Exception as err:
            print(f"[parse_market] Caught exception: {err}")
            print("exception while handling object:", market_object)

    @staticmethod
    def __parse_nested_event(event_object: dict()) -> PolymarketEvent:
        print("[parse_nested_event] called with:", event_object)
        try:
            if "tags" in event_object:
                print("tags here", event_object["tags"])
                tags: list[Tag] = []
                for tag in event_object["tags"]:
                    tags.append(Tag(**tag))
                event_object["tags"] = tags

            return PolymarketEvent(**event_object)
        except Exception as err:
            print(f"[parse_event] Caught exception: {err}")
            print("\n", event_object)


if __name__ == "__main__":
    gc = GammaMarketClient()
    b = gc.get_markets(querystring_params={"limit": 40})
    a = 1
