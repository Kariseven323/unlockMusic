package common

import (
	"reflect"
	"testing"
)

func TestParseFilenameMeta(t *testing.T) {

	tests := []struct {
		name     string
		wantMeta AudioMeta
	}{
		{
			name:     "test1",
			wantMeta: &filenameMeta{title: "test1"},
		},
		{
			name:     "周杰伦 - 晴天.flac",
			wantMeta: &filenameMeta{artists: []string{"周杰伦"}, title: "晴天"},
		},
		{
			name:     "Alan Walker _ Iselin Solheim - Sing Me to Sleep.flac",
			wantMeta: &filenameMeta{artists: []string{"Alan Walker", "Iselin Solheim"}, title: "Sing Me to Sleep"},
		},
		{
			name:     "Christopher,Madcon - Limousine.flac",
			wantMeta: &filenameMeta{artists: []string{"Christopher", "Madcon"}, title: "Limousine"},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if gotMeta := ParseFilenameMeta(tt.name); !reflect.DeepEqual(gotMeta, tt.wantMeta) {
				t.Errorf("ParseFilenameMeta() = %v, want %v", gotMeta, tt.wantMeta)
			}
		})
	}
}

// {{RIPER-5+SMART-6:
//   Action: "Parallel-Added"
//   Task_ID: "enhance-metadata-logic"
//   Timestamp: "2025-08-09T17:49:46+08:00"
//   Authoring_Subagent: "PM-direct"
//   Principle_Applied: "SOLID-S (单一职责原则)"
//   Quality_Check: "完整测试覆盖，验证智能文件名解析功能。"
// }}
// {{START_MODIFICATIONS}}

// mockAudioMeta for testing
type mockAudioMeta struct {
	title   string
	artists []string
	album   string
}

func (m *mockAudioMeta) GetTitle() string {
	return m.title
}

func (m *mockAudioMeta) GetArtists() []string {
	return m.artists
}

func (m *mockAudioMeta) GetAlbum() string {
	return m.album
}

func TestEnhanceTitleFromFilename(t *testing.T) {
	tests := []struct {
		name          string
		filename      string
		originalMeta  AudioMeta
		expectedTitle string
	}{
		{
			name:     "enhance live version",
			filename: "晴天（live）- 周杰伦.mflac",
			originalMeta: &mockAudioMeta{
				title:   "晴天",
				artists: []string{"周杰伦"},
				album:   "叶惠美",
			},
			expectedTitle: "晴天（live）",
		},
		{
			name:     "enhance remix version",
			filename: "Shape of You (Remix) - Ed Sheeran.mp3",
			originalMeta: &mockAudioMeta{
				title:   "Shape of You",
				artists: []string{"Ed Sheeran"},
				album:   "÷",
			},
			expectedTitle: "Shape of You (Remix)",
		},
		{
			name:     "multiple separators",
			filename: "Alan Walker _ Iselin Solheim - Sing Me to Sleep (Official Video).flac",
			originalMeta: &mockAudioMeta{
				title:   "Sing Me to Sleep",
				artists: []string{"Alan Walker", "Iselin Solheim"},
				album:   "Different World",
			},
			expectedTitle: "Sing Me to Sleep (Official Video)",
		},
		{
			name:     "no enhancement needed",
			filename: "晴天 - 周杰伦.flac",
			originalMeta: &mockAudioMeta{
				title:   "晴天",
				artists: []string{"周杰伦"},
				album:   "叶惠美",
			},
			expectedTitle: "晴天",
		},
		{
			name:     "complex filename with multiple dashes",
			filename: "Taylor Swift - Anti-Hero - Midnights - Deluxe Edition.mp3",
			originalMeta: &mockAudioMeta{
				title:   "Anti-Hero",
				artists: []string{"Taylor Swift"},
				album:   "Midnights",
			},
			expectedTitle: "Anti-Hero", // Should find exact match
		},
		{
			name:          "nil metadata",
			filename:      "test.mp3",
			originalMeta:  nil,
			expectedTitle: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := EnhanceTitleFromFilename(tt.originalMeta, tt.filename)

			if tt.originalMeta == nil {
				if result != nil {
					t.Errorf("expected nil result for nil input, got %v", result)
				}
				return
			}

			if result == nil {
				t.Errorf("expected non-nil result, got nil")
				return
			}

			actualTitle := result.GetTitle()
			if actualTitle != tt.expectedTitle {
				t.Errorf("expected title %q, got %q", tt.expectedTitle, actualTitle)
			}

			// Verify other metadata is preserved
			if !reflect.DeepEqual(result.GetArtists(), tt.originalMeta.GetArtists()) {
				t.Errorf("artists not preserved: expected %v, got %v",
					tt.originalMeta.GetArtists(), result.GetArtists())
			}

			if result.GetAlbum() != tt.originalMeta.GetAlbum() {
				t.Errorf("album not preserved: expected %q, got %q",
					tt.originalMeta.GetAlbum(), result.GetAlbum())
			}
		})
	}
}

func TestSplitFilename(t *testing.T) {
	tests := []struct {
		name     string
		filename string
		expected []string
	}{
		{
			name:     "simple dash separator",
			filename: "晴天（live）- 周杰伦",
			expected: []string{"晴天（live）", "周杰伦"},
		},
		{
			name:     "multiple separators",
			filename: "Alan Walker _ Iselin Solheim - Sing Me to Sleep",
			expected: []string{"Alan Walker _ Iselin Solheim", "Sing Me to Sleep"}, // " - " has priority
		},
		{
			name:     "pipe separator",
			filename: "Artist | Song | Album",
			expected: []string{"Artist", "Song", "Album"},
		},
		{
			name:     "no separators",
			filename: "SingleWord",
			expected: []string{"SingleWord"},
		},
		{
			name:     "complex multiple dashes",
			filename: "Taylor Swift - Anti-Hero - Midnights - Deluxe Edition",
			expected: []string{"Taylor Swift", "Anti-Hero", "Midnights", "Deluxe Edition"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := splitFilename(tt.filename)
			if !reflect.DeepEqual(result, tt.expected) {
				t.Errorf("expected %v, got %v", tt.expected, result)
			}
		})
	}
}

func TestCalculateSimilarity(t *testing.T) {
	tests := []struct {
		name     string
		s1       string
		s2       string
		minScore float64
	}{
		{
			name:     "identical strings",
			s1:       "hello",
			s2:       "hello",
			minScore: 1.0,
		},
		{
			name:     "substring match",
			s1:       "hello world",
			s2:       "hello",
			minScore: 0.4,
		},
		{
			name:     "similar strings",
			s1:       "晴天",
			s2:       "晴天live",
			minScore: 0.3,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			score := calculateSimilarity(tt.s1, tt.s2)
			if score < tt.minScore {
				t.Errorf("expected similarity >= %f, got %f", tt.minScore, score)
			}
		})
	}
}

// {{END_MODIFICATIONS}}
