# PlayMyNotes


### Описание сервиса: Сервис создан для того, чтобы обучение игре на фортепиано было проще и каждый мог проверить себя.
### Задача сервиса: Распознавание нот с изображения и воспроизведение полученной мелодии.

![music-animation](https://user-images.githubusercontent.com/70280347/233595267-cc3af450-c63a-4e01-a201-c9665f3aec53.gif)


#### Для работы сервиса необходимо произвести предварительныю установку нескольких библиотек:
Подробная инструкция по установки представлена ниже:

```
sudo apt update && sudo apt -y full-upgrade
sudo add-apt-repository ppa:mscore-ubuntu/mscore3-stable
sudo apt-get update
sudo apt-get install musescore3
sudo apt install timidity
sudo apt install python3-pip
pip install streamlit
pip install streamlit-lottie
pip install music21
pip install torch torchvision
git clone https://github.com/ultralytics/yolov5
pip install -qr requirements.txt
export QT_QPA_PLATFORM=offscreen
nohup python3 -m streamlit run Home.py &
```

 ###Демонстрация работы сервиса PlayMyNotes
 
