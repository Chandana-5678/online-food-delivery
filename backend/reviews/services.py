from django.db.models import Avg
def refresh_ratings(review):
    restaurant = review.restaurant; restaurant.average_rating = restaurant.reviews.aggregate(v=Avg("rating"))["v"] or 0; restaurant.save(update_fields=["average_rating"])
    if review.food_item_id:
        food = review.food_item; food.rating = food.reviews.aggregate(v=Avg("rating"))["v"] or 0; food.save(update_fields=["rating"])
