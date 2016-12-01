# -*- coding: utf-8 -*-

import amazonproduct
import subprocess
import os
from amazonproduct.errors import AWSError
# import cPickle
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Count
from django.utils.encoding import smart_str
from .forms import ItemSearchForm, ItemLookUpForm
from .models import Products
from review_analysis.apps.crawler.models import Reviews
# from review_analysis.apps.classifier.views import extract_word_features

config = {
    'access_key': settings.AWS_ACCESS_KEY,
    'secret_key': settings.AWS_SECRET_KEY,
    'associate_tag': settings.AWS_ASSOCIATE_TAG,
    'locale': settings.AWS_PREFERED_LOCALE
}

api = amazonproduct.API(cfg=config)


# Create your views here.


def index(request):
    context = "Amazon Synthesizer.\n"
    return render(request, 'index.html',
                  {'context': context})


def search(request):
    """
    Search for products using allowed params.

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = ItemSearchForm(request.POST)

        if form.is_valid():
            product_group = form.cleaned_data['productGroup']
            manufacturer = form.cleaned_data['manufacturer']
            keywords = form.cleaned_data['keywords']
            condition = form.cleaned_data['condition']

            # Search Amazon Product API
            try:
                items = api.item_search(product_group,
                                        Manufacturer=manufacturer,
                                        Keywords=keywords, Condition=condition)
            except AWSError, e:
                message = settings.AWS_ERROR_RESPONSE
                return HttpResponse(message + str(e))
            else:
                # smart_str takes care of non-ascii characters
                inventory = []
                for item in items:
                    title = smart_str(item.ItemAttributes.Title)
                    item_id = smart_str(item.ASIN)
                    item_tuple = (title, item_id)
                    inventory.append(item_tuple)

            return render(request, 'results.html',
                          {'inventory': inventory})

    else:
        form = ItemSearchForm()

    return render(request, 'search.html', {'form': form})


# def results(request):
#     return HttpResponse("Results Page.")


def lookup(request):
    """
    Look up asin to retrieve reviews

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = ItemLookUpForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.asin = form.cleaned_data['asin']
            print post.asin
            post.reviews_url = make_url(post.asin)

            # get product title
            try:
                item_lookup = api.item_lookup(post.asin)
                for item in item_lookup.Items.Item:
                    post.product_title = smart_str(item.ItemAttributes.Title)
            except AWSError, e:
                message = settings.AWS_ERROR_RESPONSE
                return HttpResponse(message + str(e))
            else:
                # find crawler cfg
                os.chdir(settings.SCRAPY_APP_DIR)
                # scrapy crawl amazon_spider -a
                # start_url="https://www.amazon.com/product-reviews/B01FFQEMVQ/"
                cmd = 'scrapy crawl amazon_spider -a start_url="%s"' \
                      % post.reviews_url
                subprocess.call(cmd, shell=True)

                # save product
                post_obj, created = Products.objects.get_or_create(
                    asin=post.asin,
                    reviews_url=post.reviews_url,
                    product_title=post.product_title)

            # display summary from scrapped data
            if post_obj is not None:
                reviews_summary = list(Reviews.objects.filter(asin=post.asin).
                                       values('sentiment__sentiment').
                                       annotate(total=Count('asin')).
                                       order_by('sentiment__sentiment'))
                total_reviews = Reviews.objects.filter(asin=post.asin).count()
                product_title = (Products.objects.get(asin__exact=post.asin)).\
                    product_title
                asin = post.asin

                return_dict = {
                    'asin': asin,
                    'product_title': product_title,
                    'total_reviews_extracted': total_reviews,
                    'sentiment_analysis': reviews_summary
                }

                return render(request, 'summary.html',
                              {'return_dict': return_dict})

    else:
        form = ItemLookUpForm()

    return render(request, 'lookup.html', {'form': form})


def make_url(asin):
    # https://www.amazon.com/product-reviews/B01H7XOSGO/
    return "https://www.amazon.com/product-reviews/" + asin + "/"





