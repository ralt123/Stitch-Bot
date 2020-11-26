"""
Unit tests for the steamHandler object. Testing it highly limited due to the dynamic nature of APIs making the
exact output data unpredictable.

For a signification portion of tests, the returned data type is evaluated to allow testing on methods of which
utilize highly dynamic data from the steam API.

Some functions are excluded from testing due to their unpredictability.
"""

from unittest import TestCase
from Steam_API import steamHandler

class Steam_API_TestCases(TestCase):
    def test_time_conversion(self):
        self.assertEqual(steamHandler._unixToUTC(473310292), [31, 12, 1984, 3, 4, 52])
        self.assertEqual(steamHandler._unixToUTC(536457600), [1, 1, 1987, 0, 0, 0])
        self.assertEqual(steamHandler._unixToUTC(951782400), [29, 2, 2000, 0, 0, 0])
        self.assertEqual(steamHandler._unixToUTC(1053668635), [23, 5, 2003, 5, 43, 55])

    def test_player_count(self):
        self.assertIsInstance(steamHandler.gamePlayerCount(730), int, "Expected integer")
        self.assertIsInstance(steamHandler.gamePlayerCount(252950), int, "Expected integer")
        self.assertFalse(steamHandler.gamePlayerCount("invalidID"), "Expected False")

    def test_find_gameID(self):
        self.assertEqual(steamHandler.findGameID("Rocket League"), 252950, "findGameID error")
        self.assertEqual(steamHandler.findGameID("counterstrike GLOBALofFensive"), 730, "findGameID error")

    def test_game_description(self):
        self.assertIsInstance(steamHandler.gameDescription(730), str, "Expected string")
        self.assertIsInstance(steamHandler.gameDescription(252950), str, "Expected string")

    def test_get_userID(self):
        self.assertEqual(steamHandler.getUserSteamID("randomuser"), "76561197999060183", "get userID failure")
        self.assertEqual(steamHandler.getUserSteamID("noavatar"), "76561198228769940", "get userID failure")

    def test_get_stats(self):
        self.assertIsInstance(steamHandler.getCSGOStats(76561198023414915), dict)

    def test_get_price(self):
        self.assertIsInstance(steamHandler.getGamePrice(730), dict)
        self.assertIsInstance(steamHandler.getGamePrice(8930), dict)

    def test_string_comparison_prep(self):
        self.assertEqual(steamHandler.stringForComparison("aN exAMPLE mEsSaGe!!??"), "anexamplemessage", "String comparison prepartion failure")
        self.assertEqual(steamHandler.stringForComparison("h3!!0 ch@t bot."), "h30chtbot", "String comparison prepartion failure")

    def test_get_friends(self):
        self.assertIsInstance(steamHandler.getFriends(76561198023414915), list, "get friends failure")

    def test_get_game_name(self):
        self.assertEqual(steamHandler.getGameName(730), "Counter-Strike: Global Offensive", "get game name failure")
        self.assertEqual(steamHandler.getGameName(8930), "Sid Meier's Civilization® V", "get game name failure")

if __name__=="__main__":
    unittest.main()
