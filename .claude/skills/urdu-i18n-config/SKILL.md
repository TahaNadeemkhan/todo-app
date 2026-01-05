---
name: urdu-i18n-config
description: Generate Urdu language internationalization (i18n) configuration for Next.js and FastAPI applications. Enables bilingual English/Urdu support for +100 bonus points.
---

# Urdu Internationalization (i18n) Configuration

## Overview

This skill generates complete bilingual (English/Urdu) internationalization setup for Phase 5 todo application. It provides translation files, configuration, and RTL (Right-to-Left) support for Next.js frontend and FastAPI backend to secure +100 bonus points.

## When to Use This Skill

- Adding Urdu language support to fulfill hackathon bonus requirement
- Implementing bilingual UI for Pakistani/South Asian users
- Setting up RTL (Right-to-Left) layout for Urdu text
- Creating translation files for all UI strings
- Configuring language switcher in application

## Core Components Generated

### 1. Next.js Frontend i18n
- `next-i18next` configuration
- Translation JSON files (en.json, ur.json)
- Language switcher component
- RTL CSS support
- Locale-aware routing

### 2. FastAPI Backend i18n
- `gettext` or `Babel` configuration
- Translation files for API responses
- Error messages in both languages
- Email templates in Urdu
- Notification messages in Urdu

### 3. Translation Files
- UI strings (buttons, labels, placeholders)
- Validation messages
- Success/error messages
- Email templates
- Push notification messages

## Usage

### Generate Complete i18n Setup

```bash
/urdu-i18n-config \
  --frontend=nextjs \
  --backend=fastapi \
  --languages=en,ur \
  --output=todo_app/phase_5/
```

### Generate Translation Files Only

```bash
/urdu-i18n-config \
  --type=translations \
  --languages=en,ur \
  --output=locales/
```

## Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `--frontend` | Frontend framework | nextjs, react |
| `--backend` | Backend framework | fastapi, express |
| `--languages` | Supported languages | en,ur |
| `--default-lang` | Default language | en |
| `--rtl-support` | Enable RTL layout | true, false |
| `--type` | Config type | all, translations, components |
| `--output` | Output directory | locales/ |

## Translation Coverage

### UI Components
- Navigation menu (Home, Tasks, Settings)
- Task form (Add Task, Title, Description, Priority, Due Date)
- Task list (All Tasks, Today, Upcoming, Completed)
- Filter/Sort controls
- Action buttons (Save, Cancel, Delete, Edit)
- Status messages (Success, Error, Loading)

### Business Logic
- Task priorities (High → زیادہ, Medium → درمیانہ, Low → کم)
- Task status (Pending → زیر التواء, Completed → مکمل)
- Recurrence patterns (Daily → روزانہ, Weekly → ہفتہ وار, Monthly → ماہانہ)
- Notifications (Task due → کام کی آخری تاریخ)

### Error Messages
- Validation errors (Required field → لازمی خانہ)
- Network errors (Connection failed → کنکشن ناکام)
- Authentication errors (Invalid credentials → غلط تفصیلات)

## RTL Support

### CSS Configuration
- Flip layout direction for Urdu
- Mirror flex/grid layouts
- Adjust padding/margin for RTL
- Handle icons and images

### Typography
- Use Urdu-compatible fonts (Noto Nastaliq Urdu, Jameel Noori Nastaleeq)
- Adjust line height for Nastaliq script
- Handle mixed English/Urdu text

## Language Switcher

### Frontend Component
- Dropdown or toggle button
- Persists user preference in localStorage/cookies
- Updates all UI instantly on switch
- Shows current language flag/name

### Backend Support
- Accept `Accept-Language` header
- Return responses in requested language
- Default to English if language not supported

## Implementation Best Practices

### 1. Complete Coverage
- Translate ALL user-facing strings
- Don't leave any English-only text
- Include pluralization rules for Urdu
- Handle date/time formatting

### 2. Cultural Adaptation
- Use appropriate Urdu terminology
- Respect Pakistani/Islamic conventions
- Format numbers using Eastern Arabic numerals (optional)
- Handle calendar differences (Gregorian/Hijri)

### 3. Testing
- Test all pages in both languages
- Verify RTL layout correctness
- Check font rendering
- Test language switcher thoroughly

### 4. Performance
- Lazy load translations
- Cache translation files
- Use efficient lookup mechanisms
- Minimize bundle size impact

## Common Urdu Translations

### Task Management
- Task → کام
- Add Task → کام شامل کریں
- Edit Task → کام میں ترمیم کریں
- Delete Task → کام حذف کریں
- Mark as Complete → مکمل کے طور پر نشان زد کریں
- Due Date → آخری تاریخ
- Priority → ترجیح
- Tags → ٹیگز
- Description → تفصیل

### Time-related
- Today → آج
- Tomorrow → کل
- Yesterday → کل
- This Week → اس ہفتے
- Next Week → اگلے ہفتے
- Overdue → میعاد ختم

### Actions
- Save → محفوظ کریں
- Cancel → منسوخ کریں
- Search → تلاش کریں
- Filter → فلٹر کریں
- Sort → ترتیب دیں
- Settings → ترتیبات

For complete translation files, React components, and configuration examples, see [examples.md](examples.md).

## Related Skills

- **nextjs-app-router**: Integrate i18n with Next.js routing
- **fastapi-design**: Add i18n to API responses
- **deployment-blueprint**: Configure i18n for production

## Tags

urdu, i18n, internationalization, translation, rtl, bilingual, localization, next-i18next, language
