# Accessibility Audit Checklist

This document outlines accessibility requirements and testing procedures for WCAG 2.1 AA compliance.

## Required Standards

### 1. Perceivable
- [ ] **Text Alternatives**: All images have alt text or aria-labels
- [ ] **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- [ ] **Resize Text**: Content readable at 200% zoom without horizontal scroll
- [ ] **Color Independence**: Information not conveyed by color alone

### 2. Operable
- [ ] **Keyboard Navigation**: All interactive elements accessible via keyboard
- [ ] **Focus Visible**: Clear focus indicators on all interactive elements
- [ ] **No Keyboard Traps**: Users can navigate away from any component
- [ ] **Skip Links**: Skip to main content link available
- [ ] **Page Titles**: Unique, descriptive page titles

### 3. Understandable
- [ ] **Language**: Page language declared in HTML
- [ ] **Predictable**: Navigation and behavior consistent across pages
- [ ] **Input Assistance**: Error messages clear and helpful
- [ ] **Labels**: All form inputs have associated labels

### 4. Robust
- [ ] **Valid HTML**: No parsing errors
- [ ] **ARIA**: Proper use of ARIA attributes
- [ ] **Name, Role, Value**: All UI components have accessible names

## Testing Tools

### Automated Testing
```bash
# Install axe-core for automated accessibility testing
npm install --save-dev @axe-core/react

# Install eslint-plugin-jsx-a11y for linting
npm install --save-dev eslint-plugin-jsx-a11y
```

### Manual Testing
1. **WAVE Browser Extension**: https://wave.webaim.org/extension/
2. **axe DevTools**: https://www.deque.com/axe/devtools/
3. **Lighthouse** (built into Chrome DevTools)
4. **Keyboard Navigation**: Tab through entire page
5. **Screen Reader**: Test with NVDA (Windows) or VoiceOver (Mac)

## Component-Level Checklist

### Buttons
- [ ] `<button>` element (not div with onClick)
- [ ] Descriptive text or aria-label
- [ ] Focus visible with outline
- [ ] Disabled state indicated

### Forms
- [ ] Each input has `<label>` with `htmlFor`
- [ ] Required fields indicated
- [ ] Error messages linked to inputs with aria-describedby
- [ ] Autocomplete attributes where appropriate

### Images
- [ ] Decorative images: `alt=""` or `role="presentation"`
- [ ] Meaningful images: Descriptive alt text
- [ ] Complex images: Longer description provided

### Links
- [ ] Descriptive link text (avoid "click here")
- [ ] External links indicated
- [ ] New window/tab behavior announced

### Modals
- [ ] `role="dialog"` and `aria-modal="true"`
- [ ] Focus trapped within modal
- [ ] Close on Escape key
- [ ] Focus returned to trigger element on close
- [ ] Background content inert (aria-hidden)

### Notifications/Alerts
- [ ] `role="alert"` for important messages
- [ ] `aria-live="polite"` or "assertive" as appropriate
- [ ] Auto-dismiss announced to screen readers

### Tables
- [ ] `<th>` elements with scope attribute
- [ ] `<caption>` for table purpose
- [ ] Complex tables have proper headers association

## Color Contrast Reference

### Current Design System
| Element | Foreground | Background | Ratio | Pass? |
|---------|-----------|------------|-------|-------|
| Body text | #111827 (gray-900) | #FFFFFF (white) | 17.4:1 | ✅ AAA |
| Secondary text | #6B7280 (gray-600) | #FFFFFF (white) | 5.7:1 | ✅ AA |
| Light text | #9CA3AF (gray-400) | #FFFFFF (white) | 3.2:1 | ❌ Fails |
| Success text | #059669 (emerald-600) | #FFFFFF (white) | 3.8:1 | ⚠️ Large text only |
| Error text | #DC2626 (red-600) | #FFFFFF (white) | 5.4:1 | ✅ AA |
| Primary button | #FFFFFF (white) | #000000 (black) | 21:1 | ✅ AAA |

**Action Items**:
- Replace gray-400 text with gray-500 or darker
- Use emerald-700 for success text instead of emerald-600
- Add icons alongside color-coded information

## Keyboard Navigation Map

### Global
- **Tab**: Move to next focusable element
- **Shift + Tab**: Move to previous focusable element
- **Enter**: Activate button/link
- **Space**: Activate button, toggle checkbox
- **Escape**: Close modal/dropdown

### HomePage
- [ ] Hero CTA buttons reachable
- [ ] Tab navigation between use case examples
- [ ] Pricing cards keyboard navigable
- [ ] Footer links accessible

### LoginPage / RegisterPage
- [ ] Form fields in logical order
- [ ] Password visibility toggle keyboard accessible
- [ ] "Remember me" checkbox space-toggleable
- [ ] Submit button enter-activatable

### Dashboard (Future)
- [ ] Graph nodes keyboard selectable
- [ ] Filters keyboard operable
- [ ] Search autocomplete arrow-key navigable

## Screen Reader Testing Script

### VoiceOver (Mac)
```bash
# Enable VoiceOver
Cmd + F5

# Basic commands
Ctrl + Option + Right Arrow: Next item
Ctrl + Option + Left Arrow: Previous item
Ctrl + Option + Space: Activate
Ctrl + Option + Shift + Down: Enter group
Ctrl + Option + Shift + Up: Exit group
```

### NVDA (Windows)
```bash
# Download from: https://www.nvaccess.org/

# Basic commands
Down Arrow: Next item
Up Arrow: Previous item
Enter/Space: Activate
Insert + F7: Elements list
Insert + T: Read title
```

## Testing Checklist by Page

### HomePage
- [ ] Hero section readable and navigable
- [ ] Use case tabs keyboard operable
- [ ] Query examples have proper labels
- [ ] Demo results screen-reader friendly
- [ ] Stats section color contrast sufficient
- [ ] Pricing table properly structured
- [ ] CTA buttons have descriptive labels
- [ ] Footer navigation accessible

### LoginPage
- [ ] Form has proper heading structure
- [ ] Email field has label and type="email"
- [ ] Password field has label and show/hide toggle
- [ ] "Remember me" checkbox properly labeled
- [ ] Error messages announced to screen readers
- [ ] Loading state announced
- [ ] Links have descriptive text

### RegisterPage
- [ ] All form fields properly labeled
- [ ] Password requirements announced
- [ ] Validation errors clear and helpful
- [ ] Terms of service link descriptive

## Automated Test Setup

Create `src/setupTests.js`:
```javascript
import '@testing-library/jest-dom';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

// Test example:
// const { container } = render(<HomePage />);
// const results = await axe(container);
// expect(results).toHaveNoViolations();
```

## Common Fixes

### Issue: Div as button
```javascript
// ❌ Bad
<div onClick={handleClick}>Click me</div>

// ✅ Good
<button onClick={handleClick}>Click me</button>
```

### Issue: Missing label
```javascript
// ❌ Bad
<input type="text" placeholder="Email" />

// ✅ Good
<label htmlFor="email">Email</label>
<input id="email" type="email" />
```

### Issue: Icon-only button
```javascript
// ❌ Bad
<button><X /></button>

// ✅ Good
<button aria-label="Close">
  <X aria-hidden="true" />
</button>
```

### Issue: Color-only information
```javascript
// ❌ Bad
<span className="text-red-600">Error</span>

// ✅ Good
<span className="text-red-600">
  <AlertCircle className="inline" aria-hidden="true" />
  Error
</span>
```

## Regular Audit Schedule

- **Daily**: Run Lighthouse on new components
- **Weekly**: Keyboard navigation test on new pages
- **Sprint End**: Full WAVE audit
- **Pre-Release**: Complete screen reader test
- **Quarterly**: Third-party accessibility audit

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Checklist](https://webaim.org/standards/wcag/checklist)
- [A11Y Project](https://www.a11yproject.com/)
- [Inclusive Components](https://inclusive-components.design/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)

## Current Status

✅ **Completed**:
- Toast notifications have proper ARIA attributes
- Modals use role="dialog" and aria-modal
- Error boundary provides clear messaging
- Theme toggle has aria-label

⏳ **In Progress**:
- Comprehensive keyboard navigation testing
- Screen reader testing script execution
- Color contrast audit and fixes

❌ **Not Started**:
- Skip navigation links
- Focus management in modals
- ARIA live region optimization
- Automated testing setup
