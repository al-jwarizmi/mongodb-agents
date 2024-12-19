from datetime import datetime
from typing import Dict, List
from database.mongodb_client import MongoDB

class DataLoader:
    def __init__(self):
        print("Initializing DataLoader...")
        self.db = MongoDB()
        print("MongoDB connection established")

    def _cleanup_collections(self):
        """Drop existing collections before loading new data."""
        print("Cleaning up existing collections...")
        try:
            self.db.products.drop()
            self.db.reviews.drop()
            print("✅ Collections dropped successfully")
        except Exception as e:
            print(f"Error dropping collections: {str(e)}")

    def load_products(self):
        """Load all products from the catalog."""
        print("Loading products...")
        products = [
            {
                "id": "ultra-comfort-mattress",
                "name": "Ultra Comfort Mattress",
                "price": 1299.00,
                "type": "Hybrid (Memory Foam + Pocket Coils)",
                "height": "12 inches",
                "construction_layers": [
                    "2\" Cooling Gel Memory Foam Top Layer",
                    "2\" Responsive Comfort Foam",
                    "2\" Transition Layer",
                    "6\" Pocket Coil System (1,024 coils in Queen size)"
                ],
                "key_features": [
                    "Advanced temperature regulation with cooling gel technology",
                    "Edge-to-edge support system",
                    "Motion isolation technology",
                    "Breathable quilted cover with silver-infused fibers",
                    "CertiPUR-US® certified foams",
                    "Compatible with adjustable bed bases"
                ],
                "best_for": [
                    "Hot sleepers",
                    "Couples",
                    "Back and stomach sleepers",
                    "Those needing extra edge support"
                ],
                "available_sizes": [
                    "Twin", "Twin XL", "Full", "Queen", "King", "California King"
                ],
                "warranty": "15 years",
                "trial_period": "100 nights"
            },
            {
                "id": "performance-sport",
                "name": "Performance Sport Mattress",
                "price": 1499.00,
                "type": "Hybrid (Copper-Infused Memory Foam + Pocket Coils)",
                "height": "13 inches",
                "construction_layers": [
                    "3\" Copper-Infused Memory Foam",
                    "2\" High-Density Support Foam",
                    "8\" Zoned Pocket Coil System (1,560 coils in Queen size)"
                ],
                "key_features": [
                    "Copper-infused memory foam for muscle recovery",
                    "Zoned support for athletic bodies",
                    "Enhanced pressure relief",
                    "Superior temperature regulation",
                    "Antimicrobial protection",
                    "Reinforced edge support"
                ],
                "best_for": [
                    "Athletes and active individuals",
                    "Those with muscle soreness",
                    "Hot sleepers",
                    "Those needing targeted support"
                ],
                "available_sizes": [
                    "Twin XL", "Full", "Queen", "King", "California King"
                ],
                "warranty": "20 years",
                "trial_period": "120 nights"
            },
            {
                "id": "eco-green",
                "name": "Eco Green Mattress",
                "price": 1199.00,
                "type": "Organic Latex Hybrid",
                "height": "11 inches",
                "construction_layers": [
                    "3\" Organic Latex",
                    "2\" Organic Cotton and Wool Blend",
                    "6\" Recycled Steel Coil System"
                ],
                "key_features": [
                    "100% organic and natural materials",
                    "GOTS and GOLS certified",
                    "Chemical-free construction",
                    "Naturally temperature regulating",
                    "Biodegradable and recyclable",
                    "Sustainably sourced materials"
                ],
                "best_for": [
                    "Eco-conscious consumers",
                    "Chemical-sensitive individuals",
                    "Those preferring natural materials",
                    "All sleep positions"
                ],
                "available_sizes": [
                    "Twin", "Twin XL", "Full", "Queen", "King"
                ],
                "warranty": "25 years",
                "trial_period": "180 nights"
            },
            {
                "id": "dream-sleep",
                "name": "Dream Sleep Mattress",
                "price": 899.00,
                "type": "All-Foam",
                "height": "10 inches",
                "construction_layers": [
                    "2\" Memory Foam Comfort Layer",
                    "2\" Adaptive Support Foam",
                    "6\" High-Density Base Foam"
                ],
                "key_features": [
                    "Pressure-relieving memory foam",
                    "Open-cell foam technology for better airflow",
                    "Removable and washable cover",
                    "Zero motion transfer",
                    "CertiPUR-US® certified foams",
                    "Medium-firm feel (6/10 on firmness scale)"
                ],
                "best_for": [
                    "Side sleepers",
                    "Light to average weight sleepers",
                    "Those seeking motion isolation",
                    "Budget-conscious shoppers"
                ],
                "available_sizes": [
                    "Twin", "Full", "Queen", "King"
                ],
                "warranty": "10 years",
                "trial_period": "100 nights"
            },
            {
                "id": "luxury-cloud",
                "name": "Luxury Cloud Mattress",
                "price": 1899.00,
                "type": "Hybrid (Latex + Memory Foam + Coils)",
                "height": "14 inches",
                "construction_layers": [
                    "2\" Natural Latex Top Layer",
                    "2\" Gel-Infused Memory Foam",
                    "2\" Dynamic Response Foam",
                    "8\" Zoned Support Coil System (1,744 coils in Queen size)"
                ],
                "key_features": [
                    "Organic cotton and wool cover",
                    "Natural latex for durability and bounce",
                    "Zoned lumbar support",
                    "Enhanced edge support system",
                    "Temperature neutral design",
                    "Antimicrobial properties",
                    "GOTS and GOLS certified materials"
                ],
                "best_for": [
                    "Luxury seekers",
                    "Those with back pain",
                    "Combination sleepers",
                    "Eco-conscious consumers"
                ],
                "available_sizes": [
                    "Twin XL", "Full", "Queen", "King", "California King", "Split King"
                ],
                "warranty": "25 years",
                "trial_period": "180 nights"
            },
            {
                "id": "essential-plus",
                "name": "Essential Plus Mattress",
                "price": 699.00,
                "type": "All-Foam",
                "height": "8 inches",
                "construction_layers": [
                    "1.5\" Comfort Foam",
                    "2\" Pressure Relief Foam",
                    "4.5\" Support Core Foam"
                ],
                "key_features": [
                    "Budget-friendly option",
                    "Medium-firm support",
                    "Basic cooling properties",
                    "Lightweight and easy to move",
                    "CertiPUR-US® certified foams",
                    "Ideal for guest rooms"
                ],
                "best_for": [
                    "Guest rooms",
                    "Children's rooms",
                    "Temporary living situations",
                    "Budget shoppers"
                ],
                "available_sizes": [
                    "Twin", "Full", "Queen"
                ],
                "warranty": "5 years",
                "trial_period": "60 nights"
            }
        ]
        
        print(f"Found {len(products)} products to load")
        # Store in MongoDB
        for product in products:
            product["created_at"] = datetime.utcnow()
            try:
                result = self.db.products.replace_one(
                    {"id": product["id"]},
                    product,
                    upsert=True
                )
                print(f"Loaded product {product['id']}: {'updated' if result.modified_count else 'inserted'}")
            except Exception as e:
                print(f"Error loading product {product['id']}: {str(e)}")
            
    def load_reviews(self):
        """Load all product reviews."""
        print("Loading reviews...")
        reviews = [
            # Ultra Comfort Mattress Reviews
            {
                "product_id": "ultra-comfort-mattress",
                "customer_id": "john_d",
                "rating": 5,
                "content": "Best sleep I've had in years! Perfect balance of soft and firm, and I don't feel my partner moving at all.",
                "verified_purchase": True
            },
            {
                "product_id": "ultra-comfort-mattress",
                "customer_id": "sarah_m",
                "rating": 5,
                "content": "The cooling technology actually works - no more night sweats. Worth every penny for the comfort and temperature regulation.",
                "verified_purchase": True
            },
            {
                "product_id": "ultra-comfort-mattress",
                "customer_id": "mike_r",
                "rating": 4,
                "content": "Great mattress overall, though took about 2 weeks to fully break in. Edge support is excellent as promised.",
                "verified_purchase": True
            },
            {
                "product_id": "ultra-comfort-mattress",
                "customer_id": "emma_l",
                "rating": 5,
                "content": "Finally found relief from my back pain after trying three other mattresses. The hybrid design provides perfect support.",
                "verified_purchase": True
            },
            {
                "product_id": "ultra-comfort-mattress",
                "customer_id": "carlos_h",
                "rating": 2,
                "content": "Too firm for my liking, even after the break-in period. Delivery was prompt though.",
                "verified_purchase": True
            },
            {
                "product_id": "ultra-comfort-mattress",
                "customer_id": "lisa_p",
                "rating": 4,
                "content": "Really happy with the quality and comfort. Only giving 4 stars because the price is a bit steep.",
                "verified_purchase": True
            },
            {
                "product_id": "ultra-comfort-mattress",
                "customer_id": "david_k",
                "rating": 5,
                "content": "Exceeded expectations in every way. My wife and I are both side and back sleepers, and it works perfectly for both of us.",
                "verified_purchase": True
            },
            {
                "product_id": "ultra-comfort-mattress",
                "customer_id": "rachel_t",
                "rating": 3,
                "content": "Decent mattress but the cooling effect isn't as dramatic as advertised. Still sleeping better than on my old mattress.",
                "verified_purchase": True
            },
            {
                "product_id": "ultra-comfort-mattress",
                "customer_id": "patricia_n",
                "rating": 5,
                "content": "The motion isolation is incredible - I can't feel my husband getting up at all. Plus, the edge support makes it feel bigger than our old mattress.",
                "verified_purchase": True
            },
            {
                "product_id": "ultra-comfort-mattress",
                "customer_id": "james_b",
                "rating": 4,
                "content": "Great quality and comfort, shipping was quick. Only complaint is that it's quite heavy to move.",
                "verified_purchase": True
            },

            # Dream Sleep Mattress Reviews
            {
                "product_id": "dream-sleep",
                "customer_id": "maria_c",
                "rating": 5,
                "content": "Perfect for our guest room! Everyone who stays over asks about where we got it.",
                "verified_purchase": True
            },
            {
                "product_id": "dream-sleep",
                "customer_id": "tom_w",
                "rating": 3,
                "content": "Good value for money, but does retain some heat. Works well for my kids' rooms.",
                "verified_purchase": True
            },
            {
                "product_id": "dream-sleep",
                "customer_id": "anna_k",
                "rating": 4,
                "content": "Great pressure relief and very comfortable. Just wish it had better edge support.",
                "verified_purchase": True
            },
            {
                "product_id": "dream-sleep",
                "customer_id": "bob_m",
                "rating": 2,
                "content": "Too soft for my taste, and started to sag after 6 months. Customer service was helpful though.",
                "verified_purchase": True
            },
            {
                "product_id": "dream-sleep",
                "customer_id": "jenny_r",
                "rating": 5,
                "content": "Amazing price point for the quality. Perfect for side sleeping and the motion isolation is excellent.",
                "verified_purchase": True
            },
            {
                "product_id": "dream-sleep",
                "customer_id": "kevin_l",
                "rating": 4,
                "content": "Comfortable and good quality for the price. No off-gassing smell unlike other foam mattresses I've tried.",
                "verified_purchase": True
            },
            {
                "product_id": "dream-sleep",
                "customer_id": "sandra_p",
                "rating": 5,
                "content": "Best mattress I've owned in this price range. The memory foam really cradles my pressure points.",
                "verified_purchase": True
            },
            {
                "product_id": "dream-sleep",
                "customer_id": "michael_g",
                "rating": 1,
                "content": "Developed a permanent body impression within 3 months. Not happy with the durability.",
                "verified_purchase": True
            },
            {
                "product_id": "dream-sleep",
                "customer_id": "laura_b",
                "rating": 4,
                "content": "Nice and comfortable, especially for the price point. Delivery and setup were hassle-free.",
                "verified_purchase": True
            },
            {
                "product_id": "dream-sleep",
                "customer_id": "chris_h",
                "rating": 3,
                "content": "Decent mattress but runs a bit warm. Good for winter, not so much for summer months.",
                "verified_purchase": True
            },

            # Luxury Cloud Mattress Reviews
            {
                "product_id": "luxury-cloud",
                "customer_id": "robert_j",
                "rating": 5,
                "content": "The combination of latex and memory foam is perfect. Haven't slept this well in decades!",
                "verified_purchase": True
            },
            {
                "product_id": "luxury-cloud",
                "customer_id": "michelle_p",
                "rating": 5,
                "content": "Expensive but worth every penny. The zoned support really helps with my lower back pain.",
                "verified_purchase": True
            },
            {
                "product_id": "luxury-cloud",
                "customer_id": "william_s",
                "rating": 3,
                "content": "Very comfortable but not sure it's worth the premium price. The organic materials are nice though.",
                "verified_purchase": True
            },
            {
                "product_id": "luxury-cloud",
                "customer_id": "helen_k",
                "rating": 5,
                "content": "Finally a luxury mattress that lives up to the hype. The natural materials help me sleep better knowing I'm not breathing in chemicals.",
                "verified_purchase": True
            },
            {
                "product_id": "luxury-cloud",
                "customer_id": "george_n",
                "rating": 2,
                "content": "Too soft despite being advertised as medium-firm. The return process was easy though.",
                "verified_purchase": True
            },
            {
                "product_id": "luxury-cloud",
                "customer_id": "jessica_m",
                "rating": 5,
                "content": "Best investment in my sleep ever. The latex layer adds the perfect amount of bounce while the memory foam contours perfectly.",
                "verified_purchase": True
            },
            {
                "product_id": "luxury-cloud",
                "customer_id": "daniel_r",
                "rating": 4,
                "content": "Amazing quality and comfort, but be prepared for the weight - this is a heavy mattress.",
                "verified_purchase": True
            },
            {
                "product_id": "luxury-cloud",
                "customer_id": "emily_w",
                "rating": 5,
                "content": "Love the eco-friendly materials and the comfort is unmatched. Worth the splurge!",
                "verified_purchase": True
            },
            {
                "product_id": "luxury-cloud",
                "customer_id": "tyler_b",
                "rating": 3,
                "content": "Great mattress but had to return due to latex allergy. Customer service was excellent throughout.",
                "verified_purchase": True
            },
            {
                "product_id": "luxury-cloud",
                "customer_id": "linda_f",
                "rating": 4,
                "content": "The split king option is perfect for my adjustable base. My only complaint is the price.",
                "verified_purchase": True
            },

            # Essential Plus Mattress Reviews
            {
                "product_id": "essential-plus",
                "customer_id": "alex_t",
                "rating": 4,
                "content": "Perfect for my college apartment. Great value for the price point!",
                "verified_purchase": True
            },
            {
                "product_id": "essential-plus",
                "customer_id": "mary_s",
                "rating": 3,
                "content": "Decent quality for a guest room mattress. Nothing fancy but gets the job done.",
                "verified_purchase": True
            },
            {
                "product_id": "essential-plus",
                "customer_id": "jordan_p",
                "rating": 5,
                "content": "Surprisingly comfortable for the price. My kids love it!",
                "verified_purchase": True
            },
            {
                "product_id": "essential-plus",
                "customer_id": "nina_r",
                "rating": 2,
                "content": "A bit too firm and basic. Wish I had spent a bit more for better quality.",
                "verified_purchase": True
            },
            {
                "product_id": "essential-plus",
                "customer_id": "derek_l",
                "rating": 4,
                "content": "Great starter mattress. Easy to move and setup, perfect for temporary living.",
                "verified_purchase": True
            },
            {
                "product_id": "essential-plus",
                "customer_id": "sophie_m",
                "rating": 3,
                "content": "Does the job for occasional guest use. Wouldn't recommend for everyday use though.",
                "verified_purchase": True
            },
            {
                "product_id": "essential-plus",
                "customer_id": "rick_h",
                "rating": 4,
                "content": "Better than expected for the price point. Perfect for my teenager's room.",
                "verified_purchase": True
            },
            {
                "product_id": "essential-plus",
                "customer_id": "amanda_c",
                "rating": 1,
                "content": "Started sagging after 6 months of use. You get what you pay for.",
                "verified_purchase": True
            },
            {
                "product_id": "essential-plus",
                "customer_id": "brian_k",
                "rating": 4,
                "content": "Good value mattress for a rental property. Easy to maintain and guests find it comfortable.",
                "verified_purchase": True
            },
            {
                "product_id": "essential-plus",
                "customer_id": "tina_w",
                "rating": 3,
                "content": "Decent temporary solution while saving for a better mattress. Shipping was quick and easy.",
                "verified_purchase": True
            },

            # Performance Sport Mattress Reviews
            {
                "product_id": "performance-sport",
                "customer_id": "ryan_m",
                "rating": 5,
                "content": "Amazing recovery after intense workouts. The copper-infused foam really seems to help with muscle soreness.",
                "verified_purchase": True
            },
            {
                "product_id": "performance-sport",
                "customer_id": "tracy_l",
                "rating": 4,
                "content": "Great support and cooling features. Perfect for active people who sleep hot.",
                "verified_purchase": True
            },
            {
                "product_id": "performance-sport",
                "customer_id": "mark_d",
                "rating": 5,
                "content": "Best mattress I've found for athletic recovery. Worth the investment for serious athletes.",
                "verified_purchase": True
            },
            {
                "product_id": "performance-sport",
                "customer_id": "karen_s",
                "rating": 2,
                "content": "Expected more at this price point. The cooling features are good but found it too firm.",
                "verified_purchase": True
            },
            {
                "product_id": "performance-sport",
                "customer_id": "steve_b",
                "rating": 5,
                "content": "Finally found the perfect mattress for my training recovery. The pressure point relief is exceptional.",
                "verified_purchase": True
            },
            {
                "product_id": "performance-sport",
                "customer_id": "jennifer_a",
                "rating": 4,
                "content": "Really helps with post-workout recovery, though the price is a bit steep. The edge support is excellent.",
                "verified_purchase": True
            },
            {
                "product_id": "performance-sport",
                "customer_id": "paul_r",
                "rating": 3,
                "content": "Good mattress but the copper-infusion benefits are hard to verify. Still sleeping better than before.",
                "verified_purchase": True
            },
            {
                "product_id": "performance-sport",
                "customer_id": "diana_k",
                "rating": 5,
                "content": "As a marathon runner, this mattress has been a game-changer for my recovery. Love the cooling properties!",
                "verified_purchase": True
            },
            {
                "product_id": "performance-sport",
                "customer_id": "mike_p",
                "rating": 4,
                "content": "Very supportive and definitely helps with recovery. Removed one star because it's quite heavy to move.",
                "verified_purchase": True
            },
            {
                "product_id": "performance-sport",
                "customer_id": "sarah_j",
                "rating": 5,
                "content": "Perfect balance of support and comfort for athletic recovery. The antimicrobial properties are a great bonus.",
                "verified_purchase": True
            }
        ]
        
        print(f"Found {len(reviews)} reviews to load")
        # Store in MongoDB
        for review in reviews:
            review["created_at"] = datetime.utcnow()
            try:
                result = self.db.reviews.replace_one(
                    {
                        "product_id": review["product_id"],
                        "customer_id": review["customer_id"]
                    },
                    review,
                    upsert=True
                )
                print(f"Loaded review for product {review['product_id']} by {review['customer_id']}: {'updated' if result.modified_count else 'inserted'}")
            except Exception as e:
                print(f"Error loading review for product {review['product_id']} by {review['customer_id']}: {str(e)}")

    def load_all_data(self):
        """Load all product and review data."""
        print("Starting data load process...")
        self._cleanup_collections()  # Clean up before loading
        self.load_products()
        self.load_reviews()
        print("✅ Loaded all products and reviews successfully")