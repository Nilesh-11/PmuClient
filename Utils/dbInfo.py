init_query = '''
DO $$ 
BEGIN
    -- Check and create/update phasor_unit_type
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'phasor_unit_type') THEN
        CREATE TYPE phasor_unit_type AS (
            scale FLOAT,
            phasor_type VARCHAR(1)
        );
    ELSE
        -- Drop and recreate if structure differs
        IF EXISTS (
            SELECT 1 FROM information_schema.attributes 
            WHERE udt_name = 'phasor_unit_type'
            AND (attribute_name != 'scale' OR data_type != 'double precision')
            OR (attribute_name != 'phasor_type' OR data_type != 'character varying')
        ) THEN
            DROP TYPE phasor_unit_type CASCADE;
            CREATE TYPE phasor_unit_type AS (
                scale FLOAT,
                phasor_type VARCHAR(1)
            );
        END IF;
    END IF;

    -- Check and create/update analog_unit_type
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'analog_unit_type') THEN
        CREATE TYPE analog_unit_type AS (
            scale INTEGER,
            analog_type VARCHAR(10)
        );
    ELSE
        -- Drop and recreate if structure differs
        IF EXISTS (
            SELECT 1 FROM information_schema.attributes 
            WHERE udt_name = 'analog_unit_type'
            AND (attribute_name != 'scale' OR data_type != 'integer')
            OR (attribute_name != 'analog_type' OR data_type != 'character varying')
        ) THEN
            DROP TYPE analog_unit_type CASCADE;
            CREATE TYPE analog_unit_type AS (
                scale INTEGER,
                analog_type VARCHAR(10)
            );
        END IF;
    END IF;

    -- Check and create/update digital_unit_type
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'digital_unit_type') THEN
        CREATE TYPE digital_unit_type AS (
            word1 VARCHAR(16),
            word2 VARCHAR(16)
        );
    ELSE
        -- Drop and recreate if structure differs
        IF EXISTS (
            SELECT 1 FROM information_schema.attributes 
            WHERE udt_name = 'digital_unit_type'
            AND (attribute_name != 'word1' OR data_type != 'character varying')
            OR (attribute_name != 'word2' OR data_type != 'character varying')
        ) THEN
            DROP TYPE digital_unit_type CASCADE;
            CREATE TYPE digital_unit_type AS (
                word1 VARCHAR(16),
                word2 VARCHAR(16)
            );
        END IF;
    END IF;

    -- Check and create/update phasor_type
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'phasor_type') THEN
        CREATE TYPE phasor_type AS (
            part1 FLOAT,
            part2 FLOAT
        );
    ELSE
        -- Drop and recreate if structure differs
        IF EXISTS (
            SELECT 1 FROM information_schema.attributes 
            WHERE udt_name = 'phasor_type'
            AND (attribute_name != 'part1' OR data_type != 'double precision')
            OR (attribute_name != 'part2' OR data_type != 'double precision')
        ) THEN
            DROP TYPE phasor_type CASCADE;
            CREATE TYPE phasor_type AS (
                part1 FLOAT,
                part2 FLOAT
            );
        END IF;
    END IF;

END $$;
'''

config_table_name = "configuration_frames"
config_table_details = '''
SOC SERIAL PRIMARY KEY,
Identifier VARCHAR(128),
FrameVersion INT,
StreamID INT,
DataRate INT,
NumberOfPMU INT,
StationName VARCHAR(16)[],
DataID INT[],
PhasorNumber INT[],
PhasorUnit phasor_unit_type[],
AnalogNumber INT[],
AnalogUnit analog_unit_type[],
DigitalNumber INT[],
DigitalUnit digital_unit_type[],
PhasorChannelNames VARCHAR(16)[][],
AnalogChannelNames VARCHAR(16)[][],
DigitalChannelNames VARCHAR(16)[][],
NominalFrequency INT[],
ConfigurationChangeCount INT[]
'''

data_table_name = "data_frames"
data_table_details = '''
SOC SERIAL PRIMARY KEY,
Identifier VARCHAR(128),
NumberOfPMU INT,
StreamID INT,
StationName VARCHAR(16)[],
DataID INT[],
PhasorChannelNames VARCHAR(16)[][],
AnalogChannelNames VARCHAR(16)[][],
DigitalChannelNames VARCHAR(16)[][],
Frequency FLOAT[],
ROCOF FLOAT[],
PhasorNumber INT[],
PhasorsType VARCHAR(16)[],
Phasors phasor_type[][],
AnalogNumber INT[],
Analogs FLOAT[][],
DigitalNumber INT[],
Digitals FLOAT[][],
DataError VARCHAR(16)[],
TimeQuality VARCHAR(16)[],
PMUSync BOOLEAN[],
TriggerReason VARCHAR(24)
'''