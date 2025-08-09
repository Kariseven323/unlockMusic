package common

import (
	"path"
	"path/filepath"
	"regexp"
	"strings"
)

type filenameMeta struct {
	artists []string
	title   string
	album   string
}

func (f *filenameMeta) GetArtists() []string {
	return f.artists
}

func (f *filenameMeta) GetTitle() string {
	return f.title
}

func (f *filenameMeta) GetAlbum() string {
	return f.album
}

func ParseFilenameMeta(filename string) (meta AudioMeta) {
	partName := strings.TrimSuffix(filename, path.Ext(filename))
	items := strings.Split(partName, "-")
	ret := &filenameMeta{}

	switch len(items) {
	case 0:
		// no-op
	case 1:
		ret.title = strings.TrimSpace(items[0])
	default:
		ret.title = strings.TrimSpace(items[len(items)-1])

		for _, v := range items[:len(items)-1] {
			artists := strings.FieldsFunc(v, func(r rune) bool {
				return r == ',' || r == '_'
			})
			for _, artist := range artists {
				ret.artists = append(ret.artists, strings.TrimSpace(artist))
			}
		}
	}

	return ret
}

// {{RIPER-5+SMART-6:
//   Action: "Parallel-Added"
//   Task_ID: "enhance-metadata-logic"
//   Timestamp: "2025-08-09T17:49:46+08:00"
//   Authoring_Subagent: "PM-direct"
//   Principle_Applied: "SOLID-S (单一职责原则)"
//   Quality_Check: "智能文件名解析，支持多分隔符和模糊匹配。"
// }}
// {{START_MODIFICATIONS}}

// enhancedMeta wraps an existing AudioMeta and allows title enhancement
type enhancedMeta struct {
	original AudioMeta
	title    string
}

func (e *enhancedMeta) GetArtists() []string {
	return e.original.GetArtists()
}

func (e *enhancedMeta) GetTitle() string {
	if e.title != "" {
		return e.title
	}
	return e.original.GetTitle()
}

func (e *enhancedMeta) GetAlbum() string {
	return e.original.GetAlbum()
}

// EnhanceTitleFromFilename analyzes filename and metadata to extract the most complete song title
func EnhanceTitleFromFilename(meta AudioMeta, filename string) AudioMeta {
	if meta == nil {
		return meta
	}

	originalTitle := meta.GetTitle()
	if originalTitle == "" {
		return meta
	}

	// Extract filename without extension
	baseName := strings.TrimSuffix(filepath.Base(filename), filepath.Ext(filename))

	// Find the best matching title part from filename
	enhancedTitle := findBestTitleMatch(baseName, originalTitle)

	// If we found a better title, return enhanced metadata
	if enhancedTitle != "" && enhancedTitle != originalTitle {
		return &enhancedMeta{
			original: meta,
			title:    enhancedTitle,
		}
	}

	return meta
}

// findBestTitleMatch finds the best matching title from filename parts
func findBestTitleMatch(filename, originalTitle string) string {
	// Split filename by common separators
	parts := splitFilename(filename)
	if len(parts) == 0 {
		return ""
	}

	// Clean original title for comparison
	cleanOriginal := cleanForComparison(originalTitle)

	bestMatch := ""
	bestScore := 0.0

	for _, part := range parts {
		cleanPart := cleanForComparison(part)

		// Calculate similarity score
		score := calculateSimilarity(cleanPart, cleanOriginal)

		// Prefer parts that contain the original title as substring
		if strings.Contains(cleanPart, cleanOriginal) {
			score += 0.5
		}

		// Special handling for exact matches (case insensitive)
		if cleanPart == cleanOriginal {
			score = 1.0
		}

		if score > bestScore && score > 0.3 { // Minimum threshold
			bestScore = score
			bestMatch = strings.TrimSpace(part)
		}
	}

	return bestMatch
}

// splitFilename splits filename by various separators and cleans parts
func splitFilename(filename string) []string {
	// Common separators in music filenames, ordered by priority (longer first)
	separators := []string{" - ", " _ ", " | ", "-", "_", "|"}

	// Find the best separator to use
	for _, sep := range separators {
		if strings.Contains(filename, sep) {
			parts := strings.Split(filename, sep)
			var result []string
			for _, part := range parts {
				trimmed := strings.TrimSpace(part)
				if trimmed != "" {
					result = append(result, trimmed)
				}
			}
			if len(result) > 1 {
				return result
			}
		}
	}

	// If no separator found, return the whole filename
	return []string{strings.TrimSpace(filename)}
}

// cleanForComparison removes punctuation and normalizes text for comparison
func cleanForComparison(text string) string {
	// Remove common punctuation and normalize spaces
	cleaned := regexp.MustCompile(`[^\p{L}\p{N}\s]`).ReplaceAllString(text, "")
	cleaned = regexp.MustCompile(`\s+`).ReplaceAllString(cleaned, " ")
	return strings.ToLower(strings.TrimSpace(cleaned))
}

// calculateSimilarity calculates similarity between two strings
func calculateSimilarity(s1, s2 string) float64 {
	if s1 == s2 {
		return 1.0
	}

	if s1 == "" || s2 == "" {
		return 0.0
	}

	// Check if one is substring of another
	if strings.Contains(s1, s2) || strings.Contains(s2, s1) {
		shorter := len(s2)
		longer := len(s1)
		if len(s1) < len(s2) {
			shorter = len(s1)
			longer = len(s2)
		}
		return float64(shorter) / float64(longer)
	}

	// Simple character-based similarity
	return calculateLevenshteinSimilarity(s1, s2)
}

// calculateLevenshteinSimilarity calculates similarity using Levenshtein distance
func calculateLevenshteinSimilarity(s1, s2 string) float64 {
	distance := levenshteinDistance(s1, s2)
	maxLen := len(s1)
	if len(s2) > maxLen {
		maxLen = len(s2)
	}

	if maxLen == 0 {
		return 1.0
	}

	return 1.0 - float64(distance)/float64(maxLen)
}

// levenshteinDistance calculates the Levenshtein distance between two strings
func levenshteinDistance(s1, s2 string) int {
	r1, r2 := []rune(s1), []rune(s2)
	len1, len2 := len(r1), len(r2)

	if len1 == 0 {
		return len2
	}
	if len2 == 0 {
		return len1
	}

	matrix := make([][]int, len1+1)
	for i := range matrix {
		matrix[i] = make([]int, len2+1)
		matrix[i][0] = i
	}

	for j := 0; j <= len2; j++ {
		matrix[0][j] = j
	}

	for i := 1; i <= len1; i++ {
		for j := 1; j <= len2; j++ {
			cost := 0
			if r1[i-1] != r2[j-1] {
				cost = 1
			}

			matrix[i][j] = min(
				matrix[i-1][j]+1,      // deletion
				matrix[i][j-1]+1,      // insertion
				matrix[i-1][j-1]+cost, // substitution
			)
		}
	}

	return matrix[len1][len2]
}

func min(a, b, c int) int {
	if a < b {
		if a < c {
			return a
		}
		return c
	}
	if b < c {
		return b
	}
	return c
}

// {{END_MODIFICATIONS}}
