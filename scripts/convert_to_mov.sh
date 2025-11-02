#!/bin/bash

# Video Converter for DaVinci Resolve
# Converts MP4 videos to MOV format with H.264 codec (reasonable file size)

echo "==================================="
echo "MP4 to MOV Converter"
echo "==================================="
echo ""

# Check if input file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_video_file> [output_file]"
    echo ""
    echo "Examples:"
    echo "  $0 input.mp4"
    echo "  $0 input.mp4 output.mov"
    echo ""
    exit 1
fi

INPUT="$1"

# Check if input file exists
if [ ! -f "$INPUT" ]; then
    echo "Error: File '$INPUT' not found!"
    exit 1
fi

# Determine output filename
if [ $# -eq 2 ]; then
    OUTPUT="$2"
else
    # Create output filename by replacing extension
    BASENAME=$(basename "$INPUT")
    FILENAME="${BASENAME%.*}"
    OUTPUT="${FILENAME}.mov"
fi

echo "Input file:  $INPUT"
echo "Output file: $OUTPUT"
echo ""

# Get video info
echo "Analyzing input video..."
WIDTH=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 "$INPUT")
HEIGHT=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of default=noprint_wrappers=1:nokey=1 "$INPUT")
CODEC=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$INPUT")

echo "Resolution: ${WIDTH}x${HEIGHT}"
echo "Current codec: $CODEC"
echo ""
echo "Converting to MOV with H.264 (high quality, reasonable size)..."
echo ""

# Convert video
# Using H.264 with high quality preset and AAC audio
ffmpeg -i "$INPUT" \
    -c:v libx264 -preset slow -crf 18 \
    -c:a aac -b:a 320k \
    -movflags +faststart \
    -y "$OUTPUT"

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "Conversion completed successfully!"
    echo "==================================="
    echo ""
    echo "Output file: $OUTPUT"
    echo ""

    # Show file sizes
    INPUT_SIZE=$(du -h "$INPUT" | cut -f1)
    OUTPUT_SIZE=$(du -h "$OUTPUT" | cut -f1)
    echo "Original size: $INPUT_SIZE"
    echo "Converted size: $OUTPUT_SIZE"
    echo ""
    echo "You can now import '$OUTPUT' into DaVinci Resolve."
else
    echo ""
    echo "Error: Conversion failed!"
    exit 1
fi
