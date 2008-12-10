from praetorian.auctions.models import Auction,User,AuctionUser,Bid,get_auction_user,user_open_auctions,user_won_auctions
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from datetime import datetime

@login_required
def index(request):
    user = request.user
    au = get_auction_user(request.user)
    open_auctions = Auction.objects.filter(status="open").order_by('-modified')
    for auction in open_auctions:
        if auction.user_can_bid(user):
            auction.can_bid = True
        else:
            auction.can_bid = False
    return render_to_response("index.html",
                              dict(user=user,
                                   au=au,
                                   open_auctions=open_auctions,
                                   nobid_auctions=Auction.objects.filter(status="nobid").order_by('-modified'),
                                   closed_auctions=Auction.objects.filter(status="closed").order_by('-modified')))



@login_required
def user_page(request):
    return render_to_response("profile.html",dict(user=request.user,
                                                  open_auctions=user_open_auctions(request.user),
                                                  won_auctions=user_won_auctions(request.user),
                                                  au=get_auction_user(request.user)))

@login_required
def auction(request,auction_id):
    auction = get_object_or_404(Auction,pk=auction_id)
    return render_to_response("auction.html",
                              dict(user=request.user,
                                   au=get_auction_user(request.user),
                                   auction=auction,
                                   user_can_bid=auction.user_can_bid(request.user),
                                   user_is_auction_winner=auction.is_user_auction_winner(request.user),
                                   user_is_top_bidder=auction.is_user_top_bidder(request.user),
                                   )
                              )

@login_required
def bid(request,auction_id):
    auction = get_object_or_404(Auction,pk=auction_id)
    if not auction.user_can_bid(request.user):
        return HttpResponse("you cannot bid on this")
    bid = Bid(auction=auction,user=request.user,amount=int(auction.min_bid()))

    bid.save()
    auction.update_bids()
    return HttpResponseRedirect("/auction/%d/" % auction.id )

def check_for_winners(request):
    for auction in Auction.objects.filter(status="open"):
        if auction.should_be_closed():
            auction.status = "closed"
            auction.modified = datetime.now()
            auction.save()
    return HttpResponse("done")

def rules(request):
    return render_to_response("rules.html",dict(user=request.user))

def welcome(request):
    return render_to_response("welcome.html",dict(user=request.user))

