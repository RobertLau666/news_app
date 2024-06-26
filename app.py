import os
import sys
import newspaper
from tqdm import tqdm
from utils import config, File_Process, Timer, AbstractGenerater, ChatGPT_API


def main():
    file_process = File_Process('launch')
    logger = file_process.logger
    timer = Timer(logger)
    abs_gen = AbstractGenerater(logger, config.abs_gen_model_name)
    chatgpt_api = ChatGPT_API(logger, openai_api_key=config.openai_api_key)

    for website_name, website_url in config.website_names_urls.items():
        paper = newspaper.build(website_url, language='zh')
        categorys = paper.category_urls()
        logger.info(f"categorys nums: {len(categorys)} \ncategorys: {categorys}")

        if len(categorys) == 1: # 被看作本身就是一篇文章，分析这个链接
            article = Article(article_url, language='zh')
            article.download()
            article.parse()
        else:

        article_json = {}
        articles = paper.articles
        logger.info(f"articles nums: {len(articles)} \articles: {articles}")
        
        get_articles_record_number = 0
        for i, article in enumerate(tqdm(articles)):
            try:
                article.download()
                article.parse()
            except Exception as e:
                logger.error(f"The article parsing was wrong: {e}")
            else:
                publish_date, publish_date_is_office = timer.get_custom_publish_date(article)
                dict_item = {
                    "original_title": article.title,
                    "original_text": article.text,
                    "abstract_text": abs_gen.abstract_generater(article.text),
                    "chatgpt_api_analyse": chatgpt_api.chat_with_gpt(article.text + config.prefix_request_prompt) if config.use_chatgpt else "The function is not enabled",
                    "original_url": article.url,
                    "publish_date": publish_date,
                    "publish_date_is_office": publish_date_is_office,
                    "authors": article.authors,
                    "top_image": article.top_image,
                    "movies": article.movies,
                    "keywords": article.keywords,
                    "summary": article.summary,
                }
                article_json[str(get_articles_record_number)] = dict_item
                get_articles_record_number += 1
            if get_articles_record_number == config.MAX_ARTICLES_NUM_EVERY_WEBSITE_I_WANT_GET:
                break
            
        # save json
        file_process.save_json(article_json, f'files/json/{website_name}.json')
        

if __name__ == "__main__":
    main()
