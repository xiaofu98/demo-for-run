package main

import "fmt"

func main() {
	const n = 5
	ch := make(chan struct{})

	for i := 1; i <= n; i++ {
		go func(id int) {
			fmt.Println("Goroutine", id)
			ch <- struct{}{}
		}(i)
	}

	for i := 0; i < n; i++ {
		<-ch
	}

	fmt.Println("All goroutines finished (Channel)")
}
