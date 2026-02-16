import re
import os

# Define image URLs for each product category
fashion_images = {
    "shirt1": "https://images.unsplash.com/photo-1596777684687-4861359183d2?w=400&h=400&fit=crop",
    "dress1": "https://images.unsplash.com/photo-1595777712802-4b2e935eaf80?w=400&h=400&fit=crop",
    "jeans1": "https://images.unsplash.com/photo-1542272604-787c62d465d1?w=400&h=400&fit=crop",
    "tshirt1": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
    "hoodie1": "https://images.unsplash.com/photo-1556821552-7f41c5d440db?w=400&h=400&fit=crop",
    "shoes1": "https://images.unsplash.com/photo-1543163521-9a539c45dd15?w=400&h=400&fit=crop",
    "bag1": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=400&fit=crop",
    "scarf1": "https://images.unsplash.com/photo-1591938091816-894babe759ff?w=400&h=400&fit=crop",
}

grocery_images = {
    "apple1": "https://images.unsplash.com/photo-1560806887-1195db42f038?w=400&h=400&fit=crop",
    "carrot1": "https://images.unsplash.com/photo-1599599810694-624a5f78a5d6?w=400&h=400&fit=crop",
    "broccoli1": "https://images.unsplash.com/photo-1588291212639-dd28a54e6e15?w=400&h=400&fit=crop",
    "juice1": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=400&fit=crop",
    "milk1": "https://images.unsplash.com/photo-1563636619-e0db3814d289?w=400&h=400&fit=crop",
    "bread1": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=400&fit=crop",
    "eggs1": "https://images.unsplash.com/photo-1582748497378-38a84f912e2b?w=400&h=400&fit=crop",
    "butter1": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=400&h=400&fit=crop",
}

books_images = {
    "fiction": "https://images.unsplash.com/photo-150784272343-583f20270319?w=400&h=400&fit=crop",
    "python": "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=400&h=400&fit=crop",
    "science": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=400&h=400&fit=crop",
    "business": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=400&fit=crop",
    "mystery": "https://images.unsplash.com/photo-1507842722343-583f20270319?w=400&h=400&fit=crop",
    "history": "https://images.unsplash.com/photo-1495446815901-4d71bcdd2085?w=400&h=400&fit=crop",
    "selfhelp": "https://images.unsplash.com/photo-1507842721343-583f20270319?w=400&h=400&fit=crop",
    "fantasy": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=400&fit=crop",
}

electronics_images = {
    "phone1": "https://images.unsplash.com/photo-1511707267537-b85faf00021e?w=400&h=400&fit=crop",
    "laptop1": "https://images.unsplash.com/photo-1588872657840-790ff3bda791?w=400&h=400&fit=crop",
    "camera1": "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=400&h=400&fit=crop",
    "headphones1": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
    "watch1": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop",
    "speaker1": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop",
    "keyboard1": "https://images.unsplash.com/photo-1587829191301-5f80fcbfb387?w=400&h=400&fit=crop",
    "mouse1": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=400&h=400&fit=crop",
}

def replace_emojis_with_images(file_path, product_cache):
    """Replace emoji references with real image URLs"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace emojis in onclick attributes
    for product_id, image_url in product_cache.items():
        # Pattern to match: onclick="openModal('product_id', 'emoji', ...
        pattern = f"onclick=\"openModal\\('{product_id}', '[^']*'"
        replacement = f"onclick=\"openModal('{product_id}', '{image_url}'"
        content = re.sub(pattern, replacement, content)
        
        # Replace emoji in product-image div text
        pattern = f"<div class=\"product-image\">[^<]*</div>.*?<!-- Product [0-9]+ -->"
        # This is complex; let's use a different approach
    
    # Also replace image src in img tags
    for product_id, image_url in product_cache.items():
        # Pattern for img src
        pattern = f'src="[^"]*(?:{product_id}|emoji)[^"]*"'
        replacement = f'src="{image_url}"'
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {file_path}")

# Process each template
base_path = r"c:\raxit\python learning\python project\templates"

replace_emojis_with_images(os.path.join(base_path, "fashion.html"), fashion_images)
replace_emojis_with_images(os.path.join(base_path, "grocery.html"), grocery_images)
replace_emojis_with_images(os.path.join(base_path, "books.html"), books_images)
replace_emojis_with_images(os.path.join(base_path, "electronics.html"), electronics_images)

print("All templates updated with real product images!")
