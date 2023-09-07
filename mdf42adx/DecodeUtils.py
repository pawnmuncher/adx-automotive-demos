# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import numpy as np
from asammdf.blocks import v4_constants as v4c

def getSource(mdf, signal):    
    '''
        Extracts the source information from the MDF-4 file for a given signal
    '''

    if signal.source is not None:
        source_name = signal.source.name
        source_type = v4c.SOURCE_TYPE_TO_STRING[signal.source.source_type]
        bus_type = v4c.BUS_TYPE_TO_STRING[signal.source.bus_type]
    else:
        source_name = "Unknown"
        source_type = "Unknown"
        bus_type = "Unknown"

    try: 
        channel_group_acq_name = mdf.groups[signal.group_index].channel_group.acq_name
    except:
        channel_group_acq_name = ""

    try: 
        acq_source_name = mdf.groups[signal.group_index].channel_group.acq_source.name
    except:
        acq_source_name = ""

    try:
        acq_source_path = mdf.groups[signal.group_index].channel_group.acq_source.path
    except:
        acq_source_path = ""

    return source_name, source_type, bus_type, channel_group_acq_name, acq_source_name, acq_source_path

def extractSignalsByType(decodedSignal):
    '''
        Extracts the signals from the MDF-4 file and converts them to a numeric or string representation
        Takes into consideration numbers, strings and records (rendered as a string) 

        We have to make sure that we have the right type / storage based on the datatype.
        Trying to use the wrong type will create issues related to loss of precision.
        We have the following types in asammdf mapped to ADX:
            records -> stringSignals / decomposed
            strings -> stringSignals
            float64, float32 -> floatSignals
            uint64 -> decimalSignals
            all other ints (int8, int16, uint32) -> integerSignals AND floatSignals

    '''   
    numberOfSamples = len(decodedSignal.timestamps)

    # create an empty array for each type of signal initialized to nan or zero values
    floatSignals = np.full(numberOfSamples, np.nan, dtype=np.double)
    integerSignals = np.zeros(numberOfSamples, dtype=np.int64)
    decimalSignals = np.zeros(numberOfSamples, dtype=np.uint64)
    stringSignals = np.empty(numberOfSamples, dtype=str)

    if np.issubdtype(decodedSignal.samples.dtype, np.record):
        stringSignals = [record.pprint() for record in decodedSignal.samples]

    # Check if the value is a string or other type of object
    elif np.issubdtype(decodedSignal.samples.dtype, np.object):
        stringSignals = decodedSignal.samples.astype(str)

    # Check if decodedSignal.samples.dtype is either a float32 or a float64
    # If this is the case, we wont fill integer as we lose the decimals.
    elif np.issubdtype(decodedSignal.samples.dtype, np.floating):
        floatSignals = decodedSignal.samples

    # Check if decodedSignal.samples.dtype is a uint64. If it is, we will only set this - otherwise we can trigger a loss of precision in analysis
    elif np.issubdtype(decodedSignal.samples.dtype, np.uint64):
        decimalSignals = decodedSignal.samples
 
    # Check if decodedSignal.samples.dtype is any other integer type
    # In this case we take the risk of loss of precision, because most of the time double is more than ok to represent
    # the int values and they are more useful in analysis.
    elif np.issubdtype(decodedSignal.samples.dtype, np.integer):
        floatSignals = decodedSignal.samples
        integerSignals = decodedSignal.samples


    return floatSignals, integerSignals, decimalSignals, stringSignals