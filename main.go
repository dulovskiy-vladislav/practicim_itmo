package main

import (
	"fmt"
	"math/rand"
	"sync"
	"time"
)

const (
	SIZE   = 10_000_000
	CHUNKS = 8

	maxRandomValue = 1_000_000
)

// generateRandomElements возвращает слайс из size случайных положительных чисел.
// При size <= 0 возвращается пустой слайс.
func generateRandomElements(size int) []int {
	if size <= 0 {
		return []int{}
	}

	elements := make([]int, size)
	for i := range elements {
		elements[i] = rand.Intn(maxRandomValue) + 1
	}
	return elements
}

// maximum возвращает максимальное число в слайсе.
// Для пустого слайса возвращается 0: элементы по условию положительные.
func maximum(elements []int) int {
	if len(elements) == 0 {
		return 0
	}

	maxValue := elements[0]
	for _, value := range elements[1:] {
		if value > maxValue {
			maxValue = value
		}
	}
	return maxValue
}

// maxChunks делит слайс на CHUNKS частей, ищет максимум в каждой
// в отдельной горутине и возвращает максимум среди найденных.
func maxChunks(elements []int) int {
	if len(elements) == 0 {
		return 0
	}

	chunkSize := len(elements) / CHUNKS
	if chunkSize == 0 {
		return maximum(elements)
	}

	chunkMaximums := make([]int, CHUNKS)
	var wg sync.WaitGroup

	for i := 0; i < CHUNKS; i++ {
		start := i * chunkSize
		end := start + chunkSize
		if i == CHUNKS-1 {
			end = len(elements)
		}

		wg.Add(1)
		go func(index int, chunk []int) {
			defer wg.Done()
			chunkMaximums[index] = maximum(chunk)
		}(i, elements[start:end])
	}
	wg.Wait()

	return maximum(chunkMaximums)
}

func main() {
	fmt.Printf("Генерируем %d целых чисел\n", SIZE)
	elements := generateRandomElements(SIZE)

	fmt.Println("Ищем максимальное значение в один поток")
	start := time.Now()
	maxValue := maximum(elements)
	elapsed := time.Since(start).Microseconds()
	fmt.Printf("Максимальное значение элементов: %d\nЗатраченное время: %d мкс\n", maxValue, elapsed)

	fmt.Printf("Ищем максимальное значение в %d потоков\n", CHUNKS)
	start = time.Now()
	maxValue = maxChunks(elements)
	elapsed = time.Since(start).Microseconds()
	fmt.Printf("Максимальное значение элементов: %d\nЗатраченное время: %d мкс\n", maxValue, elapsed)
}
