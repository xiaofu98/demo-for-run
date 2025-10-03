package main

import (
	"fmt"
)

// 正确的做法是修改指针指向的值，而不是指针本身
func addOne(a *int) {
	*a = *a + 1 // 通过解引用修改值
}

func main() {
	var num int = 1 // 先声明一个变量
	a := &num       // 获取变量的地址
	addOne(a)       // 传递指针
	fmt.Println(*a) // 打印指针指向的值，应该输出2
}
