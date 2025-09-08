# Locators específicos para o Threads (Meta)
# A primeira div representa o contêiner de todas as métricas do post,
# a segunda percorre cada métrica individualmente dentro desse contêiner.
THREADS_METRICS = '//div[@class="x78zum5"]//div[@class="x6s0dn4 x17zd0t2 x78zum5 xl56j7k"]'

# Esse XPath parte da div pai que envolve apenas o link do post, 
# assim o get_attribute("href") retorna somente o link do post 
# (sem incluir o href de localização).
THREADS_POST_HREF = '//div[@class="x78zum5 x1c4vz4f x2lah0s"]//a'
# Seletor da descrição/texto do post (ainda funciona)
THREADS_DESCRIPTION = '//div[@class="x1a6qonq x6ikm8r x10wlt62 xj0a0fe x126k92a x6prxxf x7r5mf7"]'

# Seletor que captura exatamente a div com o horário do post (ainda funciona)
THREADS_DATETIME = '//div[@class="x78zum5 x1c4vz4f x2lah0s"]'

# Seletor para o corpo principal da coluna (ainda funciona)
THREADS_FEED = '//div[@aria-label="Corpo da coluna"]'

# Seletor para cada post individual no feed (ainda funciona)
THREADS_FEED_POST = '//div[@class="x1a2a7pz x1n2onr6"]'

# Locators específicos para o youtube (Google)
# Seletor para o contêiner de vídeos na página do canal (ainda funciona)
YOUTUBE_VIDEO_CONTAINER = '//div[@class="style-scope ytd-rich-grid-renderer"]//a[@id="video-title-link"]'
