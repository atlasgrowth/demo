import os
import sqlite3

# Get the absolute path to the script
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'db.sqlite3')

def fix_slugs():
    """Fix slugs by rebuilding the table with unique slugs"""
    print("Connecting to database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Get existing slugs to check for duplicates
        cursor.execute("SELECT slug FROM demo_app_prospect")
        existing_slugs = set([row[0] for row in cursor.fetchall()])
        
        # Get the username and count occurrences
        cursor.execute("SELECT username, COUNT(*) FROM demo_app_prospect GROUP BY username")
        username_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get all prospects
        cursor.execute("SELECT id, name, username FROM demo_app_prospect")
        prospects = cursor.fetchall()
        
        # Track used slugs for this operation
        used_slugs = set()
        
        # Update the slugs
        update_count = 0
        for prospect_id, name, username in prospects:
            # If multiple records have this username, add numbering
            if username_counts[username] > 1:
                # Start with no suffix and increment until we find an unused slug
                suffix = 0
                new_slug = username
                while new_slug in used_slugs or new_slug in existing_slugs:
                    suffix += 1
                    new_slug = f"{username}{suffix}"
            else:
                new_slug = username
            
            # Mark this slug as used
            used_slugs.add(new_slug)
            
            # Update the record
            try:
                cursor.execute(
                    "UPDATE demo_app_prospect SET slug = ? WHERE id = ?", 
                    (new_slug, prospect_id)
                )
                print(f"Updated {name} to slug: {new_slug}")
                update_count += 1
            except sqlite3.IntegrityError as e:
                print(f"Error updating {name}: {e}")
        
        # Commit the changes
        cursor.execute("COMMIT")
        
        # Show some examples
        cursor.execute("SELECT name, slug, username FROM demo_app_prospect LIMIT 10")
        examples = cursor.fetchall()
        print("\nSample of updated prospects:")
        for name, slug, username in examples:
            print(f"{name} (Slug: {slug}, Username: {username})")
        
        return update_count
    
    except Exception as e:
        # Rollback in case of error
        try:
            cursor.execute("ROLLBACK")
        except:
            pass
        print(f"Error: {e}")
        return 0
    
    finally:
        conn.close()

if __name__ == "__main__":
    count = fix_slugs()
    print(f"\nSuccessfully updated {count} prospects.")