package main

import "testing"

func TestGenerateRandomElements(t *testing.T) {
	tests := []struct {
		name string
		size int
		want int
	}{
		{"нулевой размер", 0, 0},
		{"отрицательный размер", -5, 0},
		{"один элемент", 1, 1},
		{"много элементов", 1000, 1000},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := generateRandomElements(tt.size)
			if got == nil {
				t.Fatal("ожидался непустой указатель на слайс, получен nil")
			}
			if len(got) != tt.want {
				t.Fatalf("длина слайса: получено %d, ожидалось %d", len(got), tt.want)
			}
			for _, value := range got {
				if value <= 0 {
					t.Fatalf("ожидались положительные числа, получено %d", value)
				}
			}
		})
	}
}

func TestMaximum(t *testing.T) {
	tests := []struct {
		name     string
		elements []int
		want     int
	}{
		{"nil-слайс", nil, 0},
		{"пустой слайс", []int{}, 0},
		{"один элемент", []int{42}, 42},
		{"максимум в начале", []int{9, 2, 3}, 9},
		{"максимум в середине", []int{1, 9, 3}, 9},
		{"максимум в конце", []int{1, 2, 9}, 9},
		{"одинаковые элементы", []int{5, 5, 5}, 5},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := maximum(tt.elements); got != tt.want {
				t.Fatalf("получено %d, ожидалось %d", got, tt.want)
			}
		})
	}
}

func TestMaxChunks(t *testing.T) {
	for _, size := range []int{0, 1, 7, 8, 9, 15, 17, 1000, 100003} {
		elements := generateRandomElements(size)
		want := maximum(elements)
		if got := maxChunks(elements); got != want {
			t.Fatalf("размер %d: получено %d, ожидалось %d", size, got, want)
		}
	}

	t.Run("максимум в последнем остатке", func(t *testing.T) {
		elements := make([]int, 20)
		for i := range elements {
			elements[i] = 1
		}
		elements[19] = 100
		if got := maxChunks(elements); got != 100 {
			t.Fatalf("получено %d, ожидалось 100", got)
		}
	})
}
