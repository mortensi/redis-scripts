import random
import string
import argparse
import redis

# python random_data.py --count 5000 --prefixes random:user,random:order,random:cache --redis-url redis://localhost:6379/0 --value hello

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_keys(prefixes, count, key_length=8):
    keys = []
    for _ in range(count):
        prefix = random.choice(prefixes)
        rand_part = generate_random_string(key_length)
        keys.append(f"{prefix}:{rand_part}")
    return keys

def store_keys_in_redis(redis_url, keys, value="1", ttl=None):
    r = redis.from_url(redis_url)
    for key in keys:
        if ttl:
            r.setex(key, ttl, value)
        else:
            r.set(key, value)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and store random Redis keys with prefixes.")
    parser.add_argument("--count", type=int, required=True, help="Number of keys to generate")
    parser.add_argument("--prefixes", type=str, required=True, help="Comma-separated list of prefixes")
    parser.add_argument("--length", type=int, default=8, help="Length of the random part of the key (default: 8)")
    parser.add_argument("--redis-url", type=str, default="redis://localhost:6379/0", help="Redis connection URL")
    parser.add_argument("--value", type=str, default="1", help="Value to store for each key (default: '1')")
    parser.add_argument("--ttl", type=int, default=None, help="Time-to-live for keys in seconds (optional)")

    args = parser.parse_args()
    prefix_list = [p.strip() for p in args.prefixes.split(",") if p.strip()]

    keys = generate_keys(prefix_list, args.count, args.length)
    store_keys_in_redis(args.redis_url, keys, args.value, args.ttl)

    print(f"{len(keys)} keys stored in Redis at {args.redis_url}")