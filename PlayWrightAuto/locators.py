# Locators específicos para o Threads (Meta)
THREADS_METRICS = '//div[@class="x78zum5"]//div[@class="x6s0dn4 x17zd0t2 x78zum5 xl56j7k"]'
"""A primeira div representa o contêiner de todas as métricas do post,
 a segunda percorre cada métrica individualmente dentro desse contêiner."""

THREADS_POST_HREF = '//div[@class="x78zum5 x1c4vz4f x2lah0s"]//a'
"""Esse XPath parte da div pai que envolve apenas o link do post, 
assim o get_attribute("href") retorna somente o link do post 
(sem incluir o href de localização)."""

THREADS_DESCRIPTION = '//div[@class="x1a6qonq x6ikm8r x10wlt62 xj0a0fe x126k92a x6prxxf x7r5mf7"]'
"""Seletor da descrição/texto do post (ainda funciona)"""

THREADS_DATETIME = '//div[@class="x78zum5 x1c4vz4f x2lah0s"]'
"""Seletor que captura exatamente a div com o horário do post (ainda funciona)"""

THREADS_FEED = '//div[@aria-label="Corpo da coluna"]'
"""Seletor para o corpo principal da coluna (ainda funciona)"""

THREADS_FEED_POST = '//div[@class="x1a2a7pz x1n2onr6"]'
"""Seletor para cada post individual no feed (ainda funciona)"""

# Locators específicos para o youtube (Google)
YOUTUBE_VIDEO_CONTAINER = '//div[@class="style-scope ytd-rich-grid-renderer"]//a[@id="video-title-link"]'
"""Seletor para o contêiner de vídeos na página do canal (ainda funciona)"""


# Locators específicos para o Twitter (Meta)
TWITTER_FEED_CONTAINER = '//section[@class="css-175oi2r"]'
"""Seletor para o contêiner principal do feed"""

TWITTER_FEED_POST = '//article[@role="article"]'
""" Seletor para cada post individual no feed"""

TWITTER_METRICS = '//div[@class="css-175oi2r r-1kbdv8c r-18u37iz r-1wtj0ep r-1ye8kvj r-1s2bzr4"]'
"""Seletor para as métricas de engajamento do post"""

TWITTER_POST_HREF = 'a:has(time)'
"""Seletor para o link do post (contém a tag <time>)"""

TWITTER_DESCRIPTION = '//div[@data-testid="tweetText"]'
"""Seletor para o texto/descrição do post"""

# Locators específicos para o TikTok
TIKTOK_FEED_CONTAINER = '//div[@id="main-content-others_homepage"]'
"""Seletor para o contêiner principal do feed"""

TIKTOK_FEED_POST = '//div[@class=\"css-1dreve0-5e6d46e3--DivContainer-5e6d46e3--StyledDivContainerV2 eip9vuq0\"]'
"""Seletor para cada post individual no feed"""

