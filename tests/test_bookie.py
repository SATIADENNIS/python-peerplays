import mock
import datetime
import unittest
from peerplays import PeerPlays
from peerplays.utils import parse_time
from peerplaysbase.operationids import getOperationNameForId
from peerplays.instance import set_shared_peerplays_instance

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ppy = PeerPlays(
            nobroadcast=True,
            # this account creates the proposal
            # proposer="init2",
            # Proposal needs to be approve within 1 hour
            # proposal_expiration=60 * 60 * 24 * 14,
            # We want to bundle many operations into a single transaction
            bundle=True,
            # Overwrite wallet to use this list of wifs only
            wif=[wif]
        )
        set_shared_peerplays_instance(self.ppy)
        self.ppy.set_default_account("init0")

    def test_sport_create(self):
        sport = [
            ["de", "Fussball"],
            ["en", "Soccer"],
        ]
        proposal = self.ppy.proposal()
        self.ppy.sport_create(sport, append_to=proposal)
        tx = self.ppy.tx()
        ops = tx["operations"]
        prop = ops[0][1]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create"
        )
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]),
            "sport_create"
        )
        self.assertEqual(
            sport,
            prop["proposed_ops"][0]["op"][1]["name"]
        )

    def test_two_sport_create(self):
        sport = [
            ["de", "Fussball"],
            ["en", "Soccer"],
        ]
        proposal = self.ppy.proposal()
        self.ppy.sport_create(sport, append_to=proposal)
        self.ppy.sport_create(sport, append_to=proposal)
        tx = self.ppy.tx()
        ops = tx["operations"]
        prop = ops[0][1]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create"
        )
        self.assertEqual(len(prop["proposed_ops"]), 2)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]),
            "sport_create"
        )
        self.assertEqual(
            sport,
            prop["proposed_ops"][0]["op"][1]["name"]
        )
        self.assertEqual(
            sport,
            prop["proposed_ops"][1]["op"][1]["name"]
        )

    def test_event_group_create(self):
        ev = [
            ["de", "1. Bundesliga"],
            ["en", "First Country League"],
        ]
        proposal = self.ppy.proposal()
        self.ppy.sport_create(["en", "testsport"], append_to=proposal)
        self.ppy.event_group_create(ev, sport_id="0.0.0", append_to=proposal)
        tx = self.ppy.tx()
        ops = tx["operations"]
        prop = ops[0][1]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create"
        )
        self.assertEqual(len(prop["proposed_ops"]), 2)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][1]["op"][0]),
            "event_group_create"
        )
        self.assertEqual(
            ev,
            prop["proposed_ops"][1]["op"][1]["name"]
        )
        self.assertEqual(
            prop["proposed_ops"][1]["op"][1]["sport_id"],
            "0.0.0"
        )

    def test_event_create(self):
        ev = [["de", "1. Bundesliga"], ["en", "First Country League"]]
        desc = [["de", "Bundesliga"], ["en", "Germany Scoccer Championship"]]
        season = [["de", "Januar 2016"], ["en", "January 2016"]]
        start = datetime.datetime(2016, 1, 1, 0, 0, 0)
        proposal = self.ppy.proposal()
        self.ppy.sport_create(["en", "testsport"], append_to=proposal)
        self.ppy.event_group_create(ev, sport_id="0.0.0", append_to=proposal)
        self.ppy.event_create(
            desc, season, start,
            event_group_id="0.0.1",
            append_to=proposal
        )
        tx = self.ppy.tx()
        ops = tx["operations"]
        prop = ops[0][1]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create"
        )
        self.assertEqual(len(prop["proposed_ops"]), 3)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][2]["op"][0]),
            "event_create"
        )
        self.assertEqual(
            desc,
            prop["proposed_ops"][2]["op"][1]["name"]
        )
        self.assertEqual(
            season,
            prop["proposed_ops"][2]["op"][1]["season"]
        )
        self.assertEqual(
            prop["proposed_ops"][2]["op"][1]["event_group_id"],
            "0.0.1"
        )
        self.assertEqual(
            parse_time(prop["proposed_ops"][2]["op"][1]["start_time"]),
            start
        )

    def test_betting_market_rules_create(self):
        name = [["en", "NHL Rules v1.0"]]
        rule = [["en", "The winner will be the team with the most points at the end of the game.  The team with fewer points will not be the winner."]]
        self.ppy.betting_market_rules_create(
            name, rule, append_to=self.ppy.proposal()
        )
        tx = self.ppy.tx()
        ops = tx["operations"]
        prop = ops[0][1]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create"
        )
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]),
            "betting_market_rules_create"
        )
        self.assertEqual(
            name,
            prop["proposed_ops"][0]["op"][1]["name"]
        )
        self.assertEqual(
            rule,
            prop["proposed_ops"][0]["op"][1]["description"]
        )

    def test_betting_market_group_create(self):
        name = [["de", "Meine Market Group"],
                ["en", "My betting market group"]]

        rule_name = [["en", "NHL Rules v1.0"]]
        rule = [["en", "The winner will be the team with the most points at the end of the game.  The team with fewer points will not be the winner."]]
        ev = [["de", "1. Bundesliga"], ["en", "First Country League"]]
        desc = [["de", "Bundesliga"], ["en", "Germany Scoccer Championship"]]
        season = [["de", "Januar 2016"], ["en", "January 2016"]]
        start = datetime.datetime(2016, 1, 1, 0, 0, 0)

        proposal = self.ppy.proposal()
        self.ppy.sport_create(["en", "testsport"], append_to=proposal)
        self.ppy.event_group_create(ev, sport_id="0.0.0", append_to=proposal)
        self.ppy.event_create(desc, season, start, event_group_id="0.0.1", append_to=proposal)
        self.ppy.betting_market_rules_create(rule_name, rule, append_to=proposal)
        self.ppy.betting_market_group_create(
            name,
            event_id="0.0.2",
            rules_id="0.0.3",
            append_to=proposal
        )
        tx = self.ppy.tx()
        ops = tx["operations"]
        prop = ops[0][1]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create"
        )
        self.assertEqual(len(prop["proposed_ops"]), 5)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][4]["op"][0]),
            "betting_market_group_create"
        )
        self.assertEqual(
            name,
            prop["proposed_ops"][4]["op"][1]["description"]
        )
        self.assertEqual(
            "0.0.2",
            prop["proposed_ops"][4]["op"][1]["event_id"]
        )
        self.assertEqual(
            "0.0.3",
            prop["proposed_ops"][4]["op"][1]["rules_id"]
        )

    def test_betting_market_create(self):
        name = [["de", "Nuernberg gewinnt"], ["en", "Nuremberg wins"]]
        cond = [["de", "Description: Fuerth gewinnt"],
                ["en", "Description: Fuerth wins"]]

        bmg_name = [["de", "Meine Market Group"],
                    ["en", "My betting market group"]]
        rule_name = [["en", "NHL Rules v1.0"]]
        rule = [["en", "The winner will be the team with the most points at the end of the game.  The team with fewer points will not be the winner."]]
        ev = [["de", "1. Bundesliga"], ["en", "First Country League"]]
        desc = [["de", "Bundesliga"], ["en", "Germany Scoccer Championship"]]
        season = [["de", "Januar 2016"], ["en", "January 2016"]]
        start = datetime.datetime(2016, 1, 1, 0, 0, 0)

        proposal = self.ppy.proposal()
        self.ppy.sport_create(["en", "testsport"], append_to=proposal)
        self.ppy.event_group_create(ev, sport_id="0.0.0", append_to=proposal)
        self.ppy.event_create(desc, season, start, event_group_id="0.0.1", append_to=proposal)
        self.ppy.betting_market_rules_create(rule_name, rule, append_to=proposal)
        self.ppy.betting_market_group_create(bmg_name, event_id="0.0.2", rules_id="0.0.3", append_to=proposal)

        self.ppy.betting_market_create(
            cond,
            name,
            group_id="0.0.4",
            append_to=proposal
        )
        tx = self.ppy.tx()
        ops = tx["operations"]
        prop = ops[0][1]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create"
        )
        self.assertEqual(len(prop["proposed_ops"]), 6)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][5]["op"][0]),
            "betting_market_create"
        )
        self.assertEqual(
            name,
            prop["proposed_ops"][5]["op"][1]["description"]
        )
        self.assertEqual(
            cond,
            prop["proposed_ops"][5]["op"][1]["payout_condition"]
        )
        self.assertEqual(
            "0.0.4",
            prop["proposed_ops"][5]["op"][1]["group_id"]
        )

    def test_betting_market_resolve(self):
        def new_refresh(self):
            dict.__init__(
                self,
                {"id": "1.20.0"}
            )

        result = [["1.21.257", "win"],
                  ["1.21.258", "not_win"],
                  ["1.21.259", "cancel"]]

        with mock.patch(
            "peerplays.bettingmarketgroup.BettingMarketGroup.refresh",
            new=new_refresh
        ):
            self.ppy.betting_market_resolve(
                "1.20.0",
                result,
                append_to=self.ppy.proposal()
            )
            tx = self.ppy.tx()
            ops = tx["operations"]
            prop = ops[0][1]
            self.assertEqual(len(ops), 1)
            self.assertEqual(
                getOperationNameForId(ops[0][0]),
                "proposal_create"
            )
            self.assertEqual(len(prop["proposed_ops"]), 1)
            self.assertEqual(
                getOperationNameForId(prop["proposed_ops"][0]["op"][0]),
                "betting_market_group_resolve"
            )
            self.assertEqual(
                "1.20.0",
                prop["proposed_ops"][0]["op"][1]["betting_market_group_id"]
            )
            self.assertEqual(
                result,
                prop["proposed_ops"][0]["op"][1]["resolutions"]
            )
