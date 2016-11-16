# -*- coding: utf-8 -*-

import scrapy
import cPickle
from django.conf import settings
from review_analysis.apps.classifier.views import extract_word_features
from review_analysis.apps.classifier.models import Sentiment
from amazon_crawler.items import AmazonCrawlerItem


class AmazonSpiderSpider(scrapy.Spider):
    """ spider to crawl product reviews from amazon.com"""
    name = "amazon_spider"
    
    def __init__(self, *args, **kwargs): 
        super(AmazonSpiderSpider, self).__init__(*args, **kwargs) 

        self.start_urls = [kwargs.get('start_url')] 

    def parse(self, response):
        yield scrapy.Request(self.start_urls[0], callback=self.parse_reviews)

    def parse_reviews(self, response):
        """
        Retrieve reviews and create `item` object to save in db
        :param response:
        :return:
        """
        classifier = load_classifier(settings.CLASSIFIER_OBJECT)

        try:            
            reviews = response.css('.review-text').xpath('string()').extract()
            
            for review in reviews:
                item = AmazonCrawlerItem()
                item['asin'] = ((self.start_urls[0]).
                                split('product-reviews')[1]).strip('/')
                item['review_text'] = review

                sentiment = sentiment_reference(
                    classifier.classify(extract_word_features(review.split()))
                )

                item['sentiment'] = Sentiment.objects.get(id=sentiment)

                yield item            

            next_page = response.\
                css("ul.a-pagination >li.a-last > a::attr('href')")

            if next_page:
                url = response.urljoin(next_page[0].extract())
                yield scrapy.Request(url, self.parse_reviews)

        except Exception, e:
            raise e


def load_classifier(f):
    """
    `settings.CLASSIFIER_OBJECT`

    Classifier saved to byte stream from `apps.classifier.views`
    to avoid retraining it every time.

    The classifier is loaded here to allow sentiment analysis
    :return: classifier object
    """
    classifier_f = open(f, "rb")
    classifier = cPickle.load(classifier_f)
    classifier_f.close()

    return classifier


def sentiment_reference(sentiment):
    """
    This function is to reflect the normalized db structure
    We store integer referencing various sentiment types

    :param sentiment: sentiment as text e.g positive
    :return: integer referencing sentiment text e.g 1
    """
    return int({
        'positive': 1,
        'negative': 2,
        'advice': 3,
        'neutral': 4,
        'none': 5  # no sentiment
    }.get(sentiment, 5))

