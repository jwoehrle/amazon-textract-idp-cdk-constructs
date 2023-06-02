import logging
import os
import boto3
import json
import csv

logger = logging.getLogger(__name__)
__version__ = "0.0.1"

dynamodb = boto3.resource('dynamodb')

def on_event(event, context):
  print(f"event: {event}")
  print(f"context: {context}")
  request_type = event['RequestType']
  if request_type == 'Create': return on_create(event)
  if request_type == 'Update': return on_update(event)
  if request_type == 'Delete': return on_delete(event)
  raise Exception("Invalid request type: %s" % request_type)

def put_item(table, document_type: str, manifest: str):
    ddb_response = table.put_item(Item={
        "DOCUMENT_TYPE": document_type,
        "CONFIG": manifest
    })
    logger.debug(ddb_response)


def on_create(event, context, table_name):
    logger.info(f"event: {event}\ncontext: {context}")
    physical_id = 'initConfiguration'
    table = dynamodb.Table(table_name)
    with open('default_config.csv') as default_config_file:
        csv_reader = csv.reader(default_config_file)
        for row in csv_reader:
            put_item(table, row[0], row[1])
    return { 'PhysicalResourceId': physical_id }


def on_update(event, context):
    
    physical_id = event["PhysicalResourceId"]
    props = event["ResourceProperties"]
    print("update resource %s with props %s" % (physical_id))



def on_delete(event, context):
    physical_id = event["PhysicalResourceId"]
    print("delete resource %s" % physical_id)


def lambda_handler(event, context):
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    logger.setLevel(log_level)
    logger.info(json.dumps(event))
    logger.debug(f"version: {__version__}")
    logger.debug(f"boto3 version: {boto3.__version__}")
    logger.info(event)
    configuration_table = os.environ.get('CONFIGURATION_TABLE', '')
    logger.info(f'CONFIGURATION_TABLE: {configuration_table}')
    if not configuration_table:
        raise ValueError(f'no CONFIGURATION_TABLE defined')
    request_type = event['RequestType'].lower()
    if request_type == 'create':
        return on_create(event=event,
                         context=context,
                         table_name=configuration_table)
    if request_type == 'update':
        return on_update(event=event, context=context)
    if request_type == 'delete':
        return on_delete(event=event, context=context)
    raise Exception(f'Invalid request type: {request_type}')
