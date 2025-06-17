#!/bin/bash
set -e

# Enhanced Multi-Language Code Formatter
# Supports Python, JavaScript, TypeScript, Java, Go, CSS, HTML, JSON, YAML

echo "🔧 Starting Smart Code Formatting..."

# Create report file
cat > format_report.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Format Results">
  <testsuite name="Code Formatting" tests="0" failures="0" errors="0" time="0">
EOF

FORMATTED_FILES="[]"
TOTAL_FILES=0
FORMATTED_COUNT=0
ERROR_COUNT=0

# Function to add test result to XML
add_test_result() {
    local file="$1"
    local status="$2"
    local message="$3"
    local time="$4"
    
    if [ "$status" = "success" ]; then
        echo "    <testcase classname=\"format\" name=\"$file\" time=\"$time\"/>" >> format_report.xml
    else
        echo "    <testcase classname=\"format\" name=\"$file\" time=\"$time\">" >> format_report.xml
        echo "      <failure message=\"$message\">$message</failure>" >> format_report.xml
        echo "    </testcase>" >> format_report.xml
    fi
}

# Function to update JSON report
update_json_report() {
    local file="$1"
    local status="$2"
    local changes="$3"
    
    FORMATTED_FILES=$(echo "$FORMATTED_FILES" | jq --arg file "$file" --arg status "$status" --arg changes "$changes" \
        '. += [{"file": $file, "status": $status, "changes": $changes}]')
}

# Get changed files in MR
if [ -n "$CI_MERGE_REQUEST_IID" ]; then
    echo "📋 Detecting changed files in MR..."
    CHANGED_FILES=$(git diff --name-only origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME...HEAD)
else
    echo "📋 Detecting changed files in recent commits..."
    CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD)
fi

if [ -z "$CHANGED_FILES" ]; then
    echo "ℹ️ No files to format"
    echo "  </testsuite>" >> format_report.xml
    echo "</testsuites>" >> format_report.xml
    echo "$FORMATTED_FILES" > formatted_files.json
    exit 0
fi

echo "📁 Files to check:"
echo "$CHANGED_FILES" | while read file; do echo "  - $file"; done

# Format Python files
if command -v black >/dev/null 2>&1 && command -v isort >/dev/null 2>&1 && command -v autopep8 >/dev/null 2>&1; then
  echo "🐍 Formatting Python files with black, isort, and autopep8..."
else
  echo "⚠️  Python formatters not installed. Installing..."
  pip install black isort autopep8
fi

for file in $(echo "$CHANGED_FILES" | grep -E '\.(py)$' || true); do
    if [ -f "$file" ]; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
        start_time=$(date +%s.%N)
        
        echo "  Processing: $file"
        
        # Create backup
        cp "$file" "$file.backup"
        
        # Format with multiple tools
        if black --line-length 88 "$file" 2>/dev/null && \
           isort "$file" 2>/dev/null && \
           autopep8 --in-place --aggressive --aggressive "$file" 2>/dev/null; then
            
            # Check if file was actually changed
            if ! cmp -s "$file" "$file.backup"; then
                echo "    ✅ Formatted successfully"
                FORMATTED_COUNT=$((FORMATTED_COUNT + 1))
                update_json_report "$file" "formatted" "true"
            else
                echo "    ✅ Already formatted"
                update_json_report "$file" "no_changes" "false"
            fi
            
            end_time=$(date +%s.%N)
            duration=$(echo "$end_time - $start_time" | bc)
            add_test_result "$file" "success" "Formatted successfully" "$duration"
        else
            echo "    ❌ Formatting failed"
            ERROR_COUNT=$((ERROR_COUNT + 1))
            # Restore backup on failure
            mv "$file.backup" "$file"
            update_json_report "$file" "error" "false"
            
            end_time=$(date +%s.%N)
            duration=$(echo "$end_time - $start_time" | bc)
            add_test_result "$file" "failure" "Formatting failed" "$duration"
        fi
        
        # Clean backup
        rm -f "$file.backup"
    fi
done

# Format JavaScript/TypeScript files
echo "📜 Formatting JavaScript/TypeScript files..."
for file in $(echo "$CHANGED_FILES" | grep -E '\.(js|jsx|ts|tsx)$' || true); do
    if [ -f "$file" ]; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
        start_time=$(date +%s.%N)
        
        echo "  Processing: $file"
        
        cp "$file" "$file.backup"
        
        if prettier --write "$file" 2>/dev/null; then
            if ! cmp -s "$file" "$file.backup"; then
                echo "    ✅ Formatted successfully"
                FORMATTED_COUNT=$((FORMATTED_COUNT + 1))
                update_json_report "$file" "formatted" "true"
            else
                echo "    ✅ Already formatted"
                update_json_report "$file" "no_changes" "false"
            fi
            
            end_time=$(date +%s.%N)
            duration=$(echo "$end_time - $start_time" | bc)
            add_test_result "$file" "success" "Formatted successfully" "$duration"
        else
            echo "    ❌ Formatting failed"
            ERROR_COUNT=$((ERROR_COUNT + 1))
            mv "$file.backup" "$file"
            update_json_report "$file" "error" "false"
            
            end_time=$(date +%s.%N)
            duration=$(echo "$end_time - $start_time" | bc)
            add_test_result "$file" "failure" "Formatting failed" "$duration"
        fi
        
        rm -f "$file.backup"
    fi
done

# Format JSON/YAML files
echo "📄 Formatting JSON/YAML files..."
for file in $(echo "$CHANGED_FILES" | grep -E '\.(json|yaml|yml)$' || true); do
    if [ -f "$file" ]; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
        start_time=$(date +%s.%N)
        
        echo "  Processing: $file"
        
        cp "$file" "$file.backup"
        
        if prettier --write "$file" 2>/dev/null; then
            if ! cmp -s "$file" "$file.backup"; then
                echo "    ✅ Formatted successfully"
                FORMATTED_COUNT=$((FORMATTED_COUNT + 1))
                update_json_report "$file" "formatted" "true"
            else
                echo "    ✅ Already formatted"
                update_json_report "$file" "no_changes" "false"
            fi
            
            end_time=$(date +%s.%N)
            duration=$(echo "$end_time - $start_time" | bc)
            add_test_result "$file" "success" "Formatted successfully" "$duration"
        else
            echo "    ❌ Formatting failed"
            ERROR_COUNT=$((ERROR_COUNT + 1))
            mv "$file.backup" "$file"
            update_json_report "$file" "error" "false"
            
            end_time=$(date +%s.%N)
            duration=$(echo "$end_time - $start_time" | bc)
            add_test_result "$file" "failure" "Formatting failed" "$duration"
        fi
        
        rm -f "$file.backup"
    fi
done

# Format CSS files
echo "🎨 Formatting CSS files..."
for file in $(echo "$CHANGED_FILES" | grep -E '\.(css|scss|sass)$' || true); do
    if [ -f "$file" ]; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
        start_time=$(date +%s.%N)
        
        echo "  Processing: $file"
        
        cp "$file" "$file.backup"
        
        if prettier --write "$file" 2>/dev/null; then
            if ! cmp -s "$file" "$file.backup"; then
                echo "    ✅ Formatted successfully"
                FORMATTED_COUNT=$((FORMATTED_COUNT + 1))
                update_json_report "$file" "formatted" "true"
            else
                echo "    ✅ Already formatted"
                update_json_report "$file" "no_changes" "false"
            fi
            
            end_time=$(date +%s.%N)
            duration=$(echo "$end_time - $start_time" | bc)
            add_test_result "$file" "success" "Formatted successfully" "$duration"
        else
            echo "    ❌ Formatting failed"
            ERROR_COUNT=$((ERROR_COUNT + 1))
            mv "$file.backup" "$file"
            update_json_report "$file" "error" "false"
            
            end_time=$(date +%s.%N)
            duration=$(echo "$end_time - $start_time" | bc)
            add_test_result "$file" "failure" "Formatting failed" "$duration"
        fi
        
        rm -f "$file.backup"
    fi
done

# Finalize XML report
sed -i "s/tests=\"0\"/tests=\"$TOTAL_FILES\"/g" format_report.xml
sed -i "s/errors=\"0\"/errors=\"$ERROR_COUNT\"/g" format_report.xml
echo "  </testsuite>" >> format_report.xml
echo "</testsuites>" >> format_report.xml

# Save JSON report
echo "$FORMATTED_FILES" > formatted_files.json

# Summary
echo ""
echo "📊 Formatting Summary:"
echo "  Total files: $TOTAL_FILES"
echo "  Formatted: $FORMATTED_COUNT"
echo "  Errors: $ERROR_COUNT"
echo "  Success rate: $(( (TOTAL_FILES - ERROR_COUNT) * 100 / (TOTAL_FILES == 0 ? 1 : TOTAL_FILES) ))%"

if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠️ Some files failed to format. Check the logs above."
    exit 1
fi

echo "✅ Code formatting completed successfully!"