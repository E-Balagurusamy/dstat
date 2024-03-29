"""
© NoobKiddies 
"""

import instaloader
import random

insta = instaloader.Instaloader()

file_path = "/storage/emulated/0/gproxy.txt"
try:
    with open(file_path, 'r') as file:
        proxies = file.readlines()
        proxies = [proxy.strip() for proxy in proxies]  # Remove trailing newline characters
        
except FileNotFoundError:
    print("Proxy file not found.")
    
def random_proxy():
    if proxies:
        return random.choice(proxies)
    else:
        print("Proxy list is empty.")
        return None

def download(url):
    try:
        proxy = random_proxy()
        insta.context._session.proxies = {'http':  proxy, 'https': proxy}
        post = instaloader.Post.from_shortcode(insta.context, url.split('/')[-2])

        download_url = post.url
        return True, "success", download_url
    except instaloader.exceptions.InstaloaderException as e:
        return False, str(e), None
        
def download(url):
    try:
        proxy = random_proxy()
        insta.context._session.proxies = {'http':  proxy, 'https': proxy}
        post = instaloader.Post.from_shortcode(insta.context, url.split('/')[-2])
        if post.typename == 'GraphVideo':
            format = "video"
            return "video", post.video_url, post.caption
        elif post.typename == 'GraphImage':            
            return "photo", post.url, post.caption        
    except Exception as e:
        return "failed", None, str(e)

def get(username):
    try:
        # Setting a random proxy
        proxy = random_proxy()
        insta.context._session.proxies = {'http':  proxy, 'https': proxy}

        profile = instaloader.Profile.from_username(insta.context, username)

        message = f"""
*Instagram OSINT*

*Username:* `{profile.username}`
*ID:* `{profile.userid}`
*Full Name:* `{profile.full_name}`
*Biography:* `{profile.biography}`
*Business Category Name:* `{profile.business_category_name}`
*External URL:* `{profile.external_url}`
*Followed by Viewer:* `{profile.followed_by_viewer}`
*Followees:* `{profile.followees}`
*Followers:* `{profile.followers}`
*Follows Viewer:* `{profile.follows_viewer}`
*Blocked by Viewer:* `{profile.blocked_by_viewer}`
*Has Blocked Viewer:* `{profile.has_blocked_viewer}`
*Has Highlight Reels:* `{profile.has_highlight_reels}`
*Has Public Story:* `{profile.has_public_story}`
*Has Requested Viewer:* `{profile.has_requested_viewer}`
*Requested by Viewer:* `{profile.requested_by_viewer}`
*Has Viewable Story:* `{profile.has_viewable_story}`
*IGTV:* `{profile.igtvcount}`
*Is Business Account:* `{profile.is_business_account}`
*Is Private Account:* `{profile.is_private}`
*Is Verified:* `{profile.is_verified}`
*Total Posts:* `{profile.mediacount}`

Join our official channel to get more updates about bots, hacking tools and related to hacking 
@NoobKiddies
"""

        url = profile.profile_pic_url
        return True, "success", url, message 

    except instaloader.exceptions.InstaloaderException:
        # username doesn't exist or error getting user info 
        # bot.send_message(id, f"Unable to fetch data, check whether the username '{username}' exists or not and try again", parse_mode="Markdown")
        return False, "InstaloaderException", None, None 
    except Exception as e:
        return False, e, None, None

