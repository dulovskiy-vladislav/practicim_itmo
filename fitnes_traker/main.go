package main

import (
	"github.com/Yandex-Practicum/go1fl-sprint7-final/internal/actioninfo"
	"github.com/Yandex-Practicum/go1fl-sprint7-final/internal/daysteps"
	"github.com/Yandex-Practicum/go1fl-sprint7-final/internal/personaldata"
	"github.com/Yandex-Practicum/go1fl-sprint7-final/internal/trainings"
)

func main() {
	person := personaldata.Personal{Name: "Андрей", Weight: 84.6, Height: 1.87}

	ds := &daysteps.DaySteps{Personal: person}
	actioninfo.Info([]string{"678,0h50m", "792,0h14m", "abc,1h", "0,1h"}, ds)

	tr := &trainings.Training{Personal: person}
	actioninfo.Info([]string{"3456,Ходьба,3h00m", "5000,Бег,0h45m", "1000,Плавание,1h", "3456,Ходьба"}, tr)
}
