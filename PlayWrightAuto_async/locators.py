import json

def load_locators():
    with open("locators.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_locators(data):
    with open("locators.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# create a json file named locators.json in the same directory with the following content:
    {
    "THREADS_METRICS": "//div[@class=\"x78zum5\"]//div[@class=\"x6s0dn4 x17zd0t2 x78zum5 xl56j7k\"]",
    "THREADS_POST_HREF": "//div[@class=\"x78zum5 x1c4vz4f x2lah0s\"]//a",
    "THREADS_DESCRIPTION": "//div[@class=\"x1a6qonq x6ikm8r x10wlt62 xj0a0fe x126k92a x6prxxf x7r5mf7\"]",
    "THREADS_DATETIME": "//div[@class=\"x78zum5 x1c4vz4f x2lah0s\"]",
    "THREADS_FEED": "//div[@aria-label=\"Corpo da coluna\"]",
    "THREADS_FEED_POST": "//div[@class=\"x1a2a7pz x1n2onr6\"]",
    "YOUTUBE_VIDEO_CONTAINER": "//div[@class=\"style-scope ytd-rich-grid-renderer\"]//a[@id=\"video-title-link\"]",
    "TWITTER_FEED_CONTAINER": "//section[@class=\"css-175oi2r\"]",
    "TWITTER_FEED_POST": "//article[@role=\"article\"]",
    "TWITTER_METRICS": "//div[@class=\"css-175oi2r r-1kbdv8c r-18u37iz r-1wtj0ep r-1ye8kvj r-1s2bzr4\"]",
    "TWITTER_POST_HREF": "a:has(time)",
    "TWITTER_DESCRIPTION": "//div[@data-testid=\"tweetText\"]",
    "TIKTOK_FEED_CONTAINER": "//div[@id=\"main-content-others_homepage\"]",
    "TIKTOK_FEED_POST": "//div[@class=\"css-1dreve0-5e6d46e3--DivContainer-5e6d46e3--StyledDivContainerV2 eip9vuq0\"]"
}