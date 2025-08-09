package ffmpeg

import (
	"bytes"
	"embed"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sync"

	"go.uber.org/zap"
)

// {{RIPER-5+SMART-6:
//   Action: "Parallel-Added"
//   Task_ID: "embed-ffmpeg-binaries"
//   Timestamp: "2025-08-09T20:39:55+08:00"
//   Authoring_Subagent: "PM-direct"
//   Principle_Applied: "SOLID-S (单一职责原则)"
//   Quality_Check: "嵌入ffmpeg二进制文件，支持自包含部署。"
// }}
// {{START_MODIFICATIONS}}

//go:embed binaries/*
var embeddedFiles embed.FS

var (
	extractedDir string
	extractOnce  sync.Once
	extractError error
	logger       *zap.Logger
)

// EmbeddedFile represents an embedded binary file
type EmbeddedFile struct {
	Name string
	Data []byte
}

// GetEmbeddedFiles returns all embedded ffmpeg files
func GetEmbeddedFiles() ([]EmbeddedFile, error) {
	var files []EmbeddedFile

	// Read all files from the embedded filesystem
	entries, err := embeddedFiles.ReadDir("binaries")
	if err != nil {
		return nil, fmt.Errorf("failed to read embedded binaries: %w", err)
	}

	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}

		fileName := entry.Name()
		filePath := "binaries/" + fileName

		data, err := embeddedFiles.ReadFile(filePath)
		if err != nil {
			return nil, fmt.Errorf("failed to read embedded file %s: %w", fileName, err)
		}

		files = append(files, EmbeddedFile{
			Name: fileName,
			Data: data,
		})
	}

	return files, nil
}

// SetLogger sets the logger for the embedded module
func SetLogger(l *zap.Logger) {
	logger = l
}

// ExtractEmbeddedBinaries extracts embedded ffmpeg binaries to a temporary directory
func ExtractEmbeddedBinaries() (string, error) {
	extractOnce.Do(func() {
		// Create a temporary directory for extracted binaries
		tempDir, err := os.MkdirTemp("", "unlock-music-ffmpeg-*")
		if err != nil {
			extractError = fmt.Errorf("failed to create temp dir: %w", err)
			return
		}

		if logger != nil {
			logger.Debug("extracting embedded ffmpeg binaries", zap.String("tempDir", tempDir))
		}

		// Extract all embedded files
		files, err := GetEmbeddedFiles()
		if err != nil {
			os.RemoveAll(tempDir)
			extractError = fmt.Errorf("failed to get embedded files: %w", err)
			return
		}

		for _, file := range files {
			filePath := filepath.Join(tempDir, file.Name)

			if err := writeEmbeddedFile(filePath, file.Data); err != nil {
				// Clean up on error
				os.RemoveAll(tempDir)
				extractError = fmt.Errorf("failed to extract %s: %w", file.Name, err)
				return
			}

			if logger != nil {
				logger.Debug("extracted embedded file",
					zap.String("file", file.Name),
					zap.String("path", filePath),
					zap.Int("size", len(file.Data)))
			}
		}

		extractedDir = tempDir
		if logger != nil {
			logger.Info("successfully extracted embedded ffmpeg binaries", zap.String("dir", extractedDir))
		}
	})

	return extractedDir, extractError
}

// writeEmbeddedFile writes embedded binary data to a file
func writeEmbeddedFile(filePath string, data []byte) error {
	// Ensure directory exists
	if err := os.MkdirAll(filepath.Dir(filePath), 0755); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	// Create and write file
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0755)
	if err != nil {
		return fmt.Errorf("failed to create file: %w", err)
	}
	defer file.Close()

	if _, err := io.Copy(file, bytes.NewReader(data)); err != nil {
		return fmt.Errorf("failed to write file: %w", err)
	}

	return nil
}

// GetFFmpegPath returns the path to the embedded ffmpeg binary
func GetFFmpegPath() (string, error) {
	dir, err := ExtractEmbeddedBinaries()
	if err != nil {
		return "", err
	}
	return filepath.Join(dir, "ffmpeg.exe"), nil
}

// GetFFprobePath returns the path to the embedded ffprobe binary
func GetFFprobePath() (string, error) {
	dir, err := ExtractEmbeddedBinaries()
	if err != nil {
		return "", err
	}
	return filepath.Join(dir, "ffprobe.exe"), nil
}

// CleanupExtractedBinaries removes the temporary directory with extracted binaries
func CleanupExtractedBinaries() error {
	if extractedDir != "" {
		if logger != nil {
			logger.Debug("cleaning up extracted ffmpeg binaries", zap.String("dir", extractedDir))
		}
		return os.RemoveAll(extractedDir)
	}
	return nil
}

// {{END_MODIFICATIONS}}
