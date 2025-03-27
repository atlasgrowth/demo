import sqlite3
import os

def update_all_slugs():
    """
    Update all prospect slugs to match username format (all lowercase, no spaces, no special characters)
    """
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    # Connect directly to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Start transaction
    cursor.execute("BEGIN TRANSACTION;")
    
    try:
        # First, create a temporary column for the new slug
        cursor.execute("ALTER TABLE demo_app_prospect ADD COLUMN new_slug TEXT;")
        
        # Set the new slug to match the username
        cursor.execute("UPDATE demo_app_prospect SET new_slug = username;")
        
        # Drop the uniqueness constraint from the slug column
        cursor.execute("CREATE TABLE demo_app_prospect_new AS SELECT * FROM demo_app_prospect;")
        cursor.execute("DROP TABLE demo_app_prospect;")
        
        # Recreate the table with the correct schema but using new_slug as slug
        cursor.execute("""
            CREATE TABLE demo_app_prospect (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(50) NOT NULL UNIQUE,
                phone VARCHAR(20) NOT NULL,
                email VARCHAR(254) NOT NULL,
                website VARCHAR(200) NOT NULL,
                address VARCHAR(255) NOT NULL,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100) NOT NULL,
                business_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                hours TEXT NOT NULL,
                rating DECIMAL NOT NULL,
                reviews_count INTEGER NOT NULL,
                logo_url VARCHAR(200) NOT NULL,
                photo_url VARCHAR(200) NOT NULL,
                demo_site_url VARCHAR(255) NOT NULL,
                primary_color VARCHAR(20) NOT NULL,
                secondary_color VARCHAR(20) NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL
            );
        """)
        
        # Copy data from the temporary table to the new table
        cursor.execute("""
            INSERT INTO demo_app_prospect
            SELECT 
                id, name, new_slug, phone, email, website, address, city, state, 
                business_type, description, hours, rating, reviews_count, 
                logo_url, photo_url, demo_site_url, primary_color, secondary_color, 
                created_at, updated_at, username, password
            FROM demo_app_prospect_new;
        """)
        
        # Drop the temporary table
        cursor.execute("DROP TABLE demo_app_prospect_new;")
        
        # Commit the transaction
        conn.commit()
        
        # Get the count of updated records
        cursor.execute("SELECT COUNT(*) FROM demo_app_prospect;")
        count = cursor.fetchone()[0]
        
        # Show some examples of the update
        cursor.execute("SELECT name, slug, username FROM demo_app_prospect LIMIT 5;")
        examples = cursor.fetchall()
        for name, slug, username in examples:
            print(f"Updated: {name} | Slug: {slug} | Username: {username}")
        
        return count
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    # Update all slugs
    count = update_all_slugs()
    print(f"\nSuccessfully updated {count} prospects.")