from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import random,string

from django.contrib import admin


class Auction(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    modified = models.DateTimeField()
    status = models.CharField(max_length=200,default="nobid") # nobid|open|closed
    url = models.URLField()        # flickr url
    square_url = models.URLField() # flickr square url
    description = models.TextField()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "http://auctions.thraxil.org/auction/%d/" % self.id

    def close_date(self):
        if self.status == "closed":
            return self.modified
        if self.status == "nobid":
            return "no bids yet."
        else:
            return self.modified + timedelta(days=7)

    def can_bid(self):
        if self.status == "closed":
            return False
        elif self.status == "nobid":
            return True
        else:
            now = datetime.now()
            if now > self.modified + timedelta(days=7):
                # auction is now closed
                self.status = "closed"
                self.save()
                return False
            else:
                return True

    def bid_increment(self):
        if self.status == "nobid":
            return 1
        delta = datetime.now() - self.modified
        return delta.days + 1

    def days_left(self):
        if self.status == "nobid":
            return "--"
        if self.status == "closed":
            return 0
        d = self.close_date() - datetime.now()
        return d.days

            
    def bids(self):
        return self.bid_set.all().order_by("-amount")

    def has_bids(self):
        return self.bid_set.all().count()

    def highest_bid(self):
        if self.has_bids():
            return self.bid_set.order_by("-amount")[0].amount
        else:
            return 0

    def min_bid(self):
        highest = self.highest_bid()
        return highest + self.bid_increment()

    def user_can_bid(self,user):
        if not self.can_bid():
            return False
        if not user.is_authenticated():
            return False
        au = get_auction_user(user)
        if au.available_points >= self.min_bid:
            return True
        else:
            return False

    def update_bids(self):
        """ called after a new bid is added """
        self.modified = datetime.now()
        self.status = "open"
        self.save()
        top_bid = self.bid_set.order_by("-amount")[0]
        top_bid.top = True
        top_bid.save()
        other_bids = self.bid_set.exclude(id=top_bid.id)
        for b in other_bids:
            b.top = False
            b.save()

    def is_user_auction_winner(self,user):
        if self.status != "closed":
            # if the auction isn't closed, no ones a winner
            return False
        top_bid = self.bid_set.order_by("-amount")[0]
        return top_bid.user.id == user.id

    def is_user_top_bidder(self,user):
        if self.status == "nobid":
            return False
        top_bid = self.bid_set.order_by("-amount")[0]
        return top_bid.user.id == user.id

    def top_bid_user_id(self):
        if self.status == "nobid":
            return -1
        top_bid = self.bid_set.order_by("-amount")[0]
        return top_bid.user.id

    def should_be_closed(self):
        if not self.status == "open":
            return False
        if datetime.now() > self.modified + timedelta(days=7):
            return True
class AuctionAdmin(admin.ModelAdmin): pass
admin.site.register(Auction, AuctionAdmin)



def user_open_auctions(user):
    top_bids = user.bid_set.all()
    auction_ids = dict()
    auctions = []
    for auction in [b.auction for b in top_bids if b.auction.status == "open"]:
        if auction.id not in auction_ids:
            auctions.append(auction)
            auction_ids[auction.id] = 1
            if auction.user_can_bid(user):
                auction.can_bid = True
            else:
                auction.can_bid = False
    return auctions

def user_won_auctions(user):
    top_bids = user.bid_set.filter(top=True)
    return [b.auction for b in top_bids if b.auction.status == "closed"]

    
class AuctionUser(models.Model):
    user   = models.ForeignKey(User)
    randid = models.CharField(max_length=200)
    points = models.PositiveIntegerField(default=50)

    def __unicode__(self):
        return self.user.__unicode__()

    def available_points(self):
        bids = self.user.bid_set.filter(top=True)
        amount_bid = sum([b.amount for b in bids])
        return self.points - amount_bid

    def can_bid_on_nobids(self):
        return self.available_points() > 0

class AuctionUserAdmin(admin.ModelAdmin): pass
admin.site.register(AuctionUser, AuctionUserAdmin)


def make_randid():
    return ''.join([random.choice(string.letters + string.digits) for i in range(20)])

def get_auction_user(user):
    """ return an AuctionUser from the User object. create if necessary """
    if user.auctionuser_set.count() > 0:
        return user.auctionuser_set.all()[0]
    else:
        if user.is_authenticated():
            au = AuctionUser(user=user,points=50,randid=make_randid())
            au.save()
            return au
        else:
            # should be some kind of dummy, i guess
            return AuctionUser(user=user,points=0)


class Bid(models.Model):
    user = models.ForeignKey(User)
    auction = models.ForeignKey(Auction)
    amount = models.PositiveIntegerField(default=1)
    top = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=datetime.now)

