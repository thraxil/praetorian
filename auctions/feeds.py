from datetime import datetime, timedelta
from django.contrib.auth.models import User
from praetorian.auctions.models import Auction,User,AuctionUser,Bid,get_auction_user,user_open_auctions,user_won_auctions
from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed

class MainFeed(Feed):
    feed_type = Atom1Feed
    title = "Auctions"
    link = "/"
    description = "Updates on auctions at auctions.thraxil.org"

    def items(self):
        return Auction.objects.order_by('-modified')[:20]
        
                        
