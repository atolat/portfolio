import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


def handler(event, context):
    body = json.loads(event.get('body', '{}'))
    cache_status = body.get('cache_status', 'UNKNOWN')
    pop = body.get('pop', 'unknown')
    today = datetime.utcnow().strftime('%Y-%m-%d')

    # Atomic increments
    updates = [
        'total_views',
        f'today:{today}',
        f'cache_{cache_status.lower()}s' if cache_status in ('HIT', 'MISS') else None,
        f'pop:{pop}' if pop != 'unknown' else None,
    ]

    for pk in filter(None, updates):
        table.update_item(
            Key={'pk': pk},
            UpdateExpression='ADD #c :inc',
            ExpressionAttributeNames={'#c': 'count'},
            ExpressionAttributeValues={':inc': 1},
        )

    # Read stats
    total = table.get_item(Key={'pk': 'total_views'}).get('Item', {}).get('count', 0)
    today_count = table.get_item(Key={'pk': f'today:{today}'}).get('Item', {}).get('count', 0)
    hits = table.get_item(Key={'pk': 'cache_hits'}).get('Item', {}).get('count', 0)
    misses = table.get_item(Key={'pk': 'cache_misses'}).get('Item', {}).get('count', 0)

    # Count unique POPs by scanning (small table, fine)
    scan = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('pk').begins_with('pop:'))
    pops = [item['pk'].split(':', 1)[1] for item in scan.get('Items', [])]

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': 'application/json',
        },
        'body': json.dumps({
            'total_views': int(total),
            'today_views': int(today_count),
            'cache_hits': int(hits),
            'cache_misses': int(misses),
            'hit_ratio': round(int(hits) / max(int(hits) + int(misses), 1), 3),
            'unique_pops': pops,
        })
    }
