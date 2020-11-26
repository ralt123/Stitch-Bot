"""
Unit tests for the twitchHandler object. Testing it highly limited due to the dynamic nature of APIs making the
exact output data unpredictable.

Some functions are excluded from testing due to their unpredictability.
"""

from unittest import TestCase
from Twitch_API import twitchHandler


# Due to the dynamic content of APIs, we must retrieve the ID of currently streaming streamers as to conduct the
# required tests. This is done by utilizing the API.
try:
    streamingStreams = twitchHandler.gameTopStreamers(111, "rocket league")
    twitchHandler.streamingStreamerID1 = twitchHandler.getStreamerID(streamingStreams[0][0])
    twitchHandler.streamingStreamerID2 = twitchHandler.getStreamerID(streamingStreams[1][0])
except:
    raise Exception("Critical error for gathering streaming streamers")


class Twitch_API_TestCases(TestCase):
    def test_retrieve_data(self):
        # checks that the inExpectedReturn dictionary is a subset of the returned dictionary
        inExpectedReturn={'display_name': 'example', 'id': '886609', 'login': 'example'}
        self.assertTrue(inExpectedReturn.items() <= twitchHandler.retrieveData("https://api.twitch.tv/helix/users?login=example")["data"][0].items(), "Critical retrieve data error")

    def test_get_streamerID(self):
        self.assertEqual(twitchHandler.getStreamerID("twitch"), "12826", "get streamer ID failure")
        self.assertEqual(twitchHandler.getStreamerID("esl"), "67834893", "get streamer ID failure")

    def test_check_if_streaming(self):
        self.assertTrue(twitchHandler.checkIfStreaming(twitchHandler.streamingStreamerID1), "Expected to be true")
        self.assertTrue(twitchHandler.checkIfStreaming(twitchHandler.streamingStreamerID2), "Expected to be true")


    def test_stream_details(self):
        self.assertEqual(twitchHandler.streamDetails(twitchHandler.streamingStreamerID1)["user_id"], twitchHandler.streamingStreamerID1, "stream details failure")
        self.assertEqual(twitchHandler.streamDetails(twitchHandler.streamingStreamerID2)["user_id"], twitchHandler.streamingStreamerID2, "stream details failure")

    def test_get_gameID(self):
        self.assertEqual(twitchHandler.getGameID("rocket league"), "30921", "get game ID failure")
        self.assertEqual(twitchHandler.getGameID("counter-strike: global offensive"), "32399", "get game ID failure")
        self.assertEqual(twitchHandler.getGameID("counter STRIKE GlOBaL ofFENsive!"), "32399", "get game ID failure")

    def test_get_streamer_name(self):
        self.assertEqual(twitchHandler.getStreamerName(12826), "twitch", "get streamer name failure")
        self.assertEqual(twitchHandler.getStreamerName(67834893), "esl", "get streamer name failure")

if __name__=="__main__":
    unittest.main()
