# Youthful Quote Generator 🌟

A dynamic and interactive quote generator built with Python and Tkinter, offering inspirational quotes across various themes with mood-based recommendations and social features.

## 📸 Screenshots:
![Screenshot](https://github.com/dundd2/Youthful-Quote-Generator/blob/main/Screenshots/SC%20(5).png)
![Screenshot](https://github.com/dundd2/Youthful-Quote-Generator/blob/main/Screenshots/SC%20(2).png)
![Screenshot](https://github.com/dundd2/Youthful-Quote-Generator/blob/main/Screenshots/SC%20(3).png)
![Screenshot](https://github.com/dundd2/Youthful-Quote-Generator/blob/main/Screenshots/SC%20(4).png)
![Screenshot](https://github.com/dundd2/Youthful-Quote-Generator/blob/main/Screenshots/SC%20(1).png)

## 🌈 Core Features

### 1. Quote Management
- **Multi-Category Library**
  - 10 categories including Courage, Friendship, Dreams, Love, Life
  - 9 curated quotes per category
  - Support for multiple languages

- **Custom Quote Feature** 
  - Add personal quotes
  - Local JSON storage for quotes

### 2. User System
- **Account Management**
  - User registration/login
  - Personal profile page
  - Achievement tracking

- **Personalization**
  - Voice settings (speed, volume)
  - Theme switching (Modern Light, Modern Dark, Pastel)
  - Interface language settings

### 3. Interactive Features
- **Mood-Based**
  - Five emotional states: Happy, Sad, Anxious, Excited, Calm
  - Mood-based quote recommendations
  
- **Social Elements**
  - Quote rating (1-5 stars)
  - Comments system
  - Social sharing (Facebook, Twitter, LinkedIn)
  - Quote favorites

### 4. Interface Design
- **Modern UI**
  - Responsive card layout
  - Smooth animations
  - Emoji integration
  - Adaptive scrolling areas

- **Visual Feedback**
  - Dynamic background colors
  - Sound effects
  - Loading animations

## 🔧 Technical Implementation

### Data Storage
- JSON format for:
  - User data
  - Custom quotes
  - Rating records
  - Comments
  - Achievements

### Frameworks & Libraries
- **GUI**: Tkinter
- **Sound**: winsound
- **Voice**: pyttsx3
- **Browser Integration**: webbrowser

## 💻 Installation Guide

1. Clone the repository:
```bash
git clone https://github.com/dundd2/youthful-quote-generator.git
cd youthful-quote-generator
```

2. Install required packages:
```bash
pip install pyttsx3
```

3. Run the application:
```bash
python main.py
```

## 💡 Usage Instructions

1. **Start the Application**
   - Launch the application
   - Register or log in to access all features

2. **Generate Quotes**
   - Select a category from the dropdown menu
   - Click the "Generate Quote" button
   - Enjoy the color-changing interface and sound effects

3. **Mood-Based Quotes**
   - Select your current mood
   - Get personalized quotes based on your emotional state

4. **Interactive Quotes**
   - Rate quotes
   - Add comments
   - Share on social media
   - Create custom quotes

## 🎨 Theme Customization

### Available Themes
- **Modern Light**
  - Clean white background
  - Soft shadows
  - Blue accent colors
  - High readability

- **Modern Dark**
  - Dark background
  - Purple accents
  - Reduced eye strain
  - Perfect for night use

- **Pastel**
  - Soft pink undertones
  - Gentle color transitions
  - Warm visual experience
  - Soothing interface

## 🎵 Audio Features

### Text-to-Speech
- Customizable voice speed
- Adjustable volume
- Multiple voice options
- Quote reading on demand

### Sound Effects
- Button click feedback
- Quote generation chimes
- Achievement unlocks
- Error notifications

## 🐛 Troubleshooting

### Common Issues
1. **Sound not working**
   - Check system volume
   - Verify audio device
   - Reinstall pyttsx3

2. **Theme not changing**
   - Restart application
   - Check display settings
   - Update Tkinter

3. **Login issues**
   - Clear user_data.json
   - Reset credentials
   - Check permissions


### Code Style
- Follow PEP 8
- Comment your code
- Keep functions simple
- Write unit tests


### Credits
- Quote database: Various public domains
- Icons: Material Design Icons
- Sounds: FreeSound.org
- Inspiration: Various quote applications
