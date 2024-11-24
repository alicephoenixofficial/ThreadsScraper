from playwright.sync_api import sync_playwright
import time
import re

def scrape_threads_followers_and_following(username, password, target_profile):
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Log in to Threads.net
        page.goto("https://www.threads.net/login")
        print("Navigating to login page...")

        # Use the input username and password from the user
        if page.locator('input[placeholder="Password"]').is_visible():
            # Handle first login page form
            page.fill('input[placeholder="Username, phone or email"]', username)
            page.fill('input[placeholder="Password"]', password)
        else:
            # Handle second login form (if there's a different layout)
            page.fill('input[autocomplete="username"]', username)
        
        page.click("div:text('Log in')")
        page.wait_for_load_state('networkidle')  # Wait until the page has finished loading (all network activity idle)
        print("Logged in successfully!")

        # Step 2: Navigate to the target user's profile
        target_url = f"https://www.threads.net/{target_profile}"
        page.goto(target_url)
        print(f"Navigated to {target_profile}'s profile.")

        # Step 3: Scrape Followers
        followers_data = []
        page.click("span:text('Followers')")
        page.wait_for_timeout(3000)
        print("Opened followers list.")

        # Scroll and scrape followers
        last_height = page.evaluate('document.documentElement.scrollHeight')

        while True:
            followers = page.locator("div.x1e4zzel:nth-child(2) > div:nth-child(1) > div:nth-child(1)")
            followers.
            follower_names = []
            for i in range(followers.count()):
                name = followers.nth(i).text_content().strip()  # Clean up the name
                if name:  # Ensure we only append non-empty names
                    follower_names.append(name)
                raw_text = followers.nth(i).text_content().strip()
                # Clean and extract username
                clean_text = re.sub(r'(Follow back|Following)$', '', raw_text).strip()
                match = re.match(r"([a-zA-Z0-9_\.]+)", clean_text)
                if match:
                    follower_names.append(match.group(1))  # Add username part
            
            # Log the scraped follower names
            print(f"Scraped {len(follower_names)} followers.")
            for name in follower_names:
                print(name)

            # Append names to the overall list
            followers_data.extend(follower_names)

            # Scroll down to load more
            page.evaluate("window.scrollBy(0, 300)")
            time.sleep(3)  # Allow time for loading new content

            # Check if scrolling loads new content
            new_height = page.evaluate('document.documentElement.scrollHeight')
            if new_height == last_height:
                print("No more followers found after scrolling.")
                break
            last_height = new_height

        followers_list = list(followers_data)  # Convert set to list for final output
        print(f"Total Followers: {len(followers_list)}")
        print(f"Total Scraped {len(followers_data)} followers.")

        # Step 4: Scrape Following
        following_data = []
        page.click("span:text('Following')")
        page.wait_for_timeout(3000)
        print("Opened following list.")

        # Scroll and scrape following
        last_height = page.evaluate('document.documentElement.scrollHeight')

        while True:
            following = page.locator("div.x12v9rci:nth-child(1) > div:nth-child(1)")
            following_names = []
            for i in range(following.count()):
                name = following.nth(i).text_content().strip()  # Clean up the name
                if name:  # Ensure we only append non-empty names
                    following_names.append(name)
                raw_text = following.nth(i).text_content().strip()
                # Clean and extract username
                clean_text = re.sub(r'(Follow back|Following)$', '', raw_text).strip()
                match = re.match(r"([a-zA-Z0-9_\.]+)", clean_text)
                if match:
                    following_names.append(match.group(1))  # Add username part
            # Log the scraped following names
            print(f"Scraped {len(following_names)} following.")
            for name in following_names:
                print(name)

            # Append names to the overall list
            following_data.extend(following_names)

            # Scroll down to load more
            page.evaluate("window.scrollBy(0, 200)")  # Scroll by 200px increment
            time.sleep(3)  # Wait a bit longer for content to load

            # Check if new content loaded
            new_height = page.evaluate('document.documentElement.scrollHeight')
            if new_height == last_height:
                print("No new following found after scrolling.")
                break  # Exit if no new content loaded
            last_height = new_height  # Update last height for next iteration

        print(f"Total Scraped {len(following_data)} following.")

        # Step 5: Close the browser
        browser.close()

        return {
            "followers": followers_data,
            "following": following_data
        }

# Main execution
if __name__ == "__main__":
    username = "@alice.phoenix.official"
    password = "Enzymic2736!"  # Ensure this is correct
    target_profile = username

    data = scrape_threads_followers_and_following(username, password, target_profile)

    print("Followers:", data["followers"])
    print("Following:", data["following"])
