// Multi-value autocomplete (for comma/semicolon separated inputs)
class MultiAutocomplete {
    constructor(inputId, dropdownId, suggestions, separator = ',') {
        this.input = document.getElementById(inputId)
        this.dropdown = document.getElementById(dropdownId)
        this.suggestions = suggestions || []
        this.separator = separator
        this.selectedIndex = -1

        if (!this.input || !this.dropdown) return

        this.input.addEventListener('input', () => this.handleInput())
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e))
        this.input.addEventListener('blur', () => setTimeout(() => this.hideDropdown(), 200))
        this.input.addEventListener('focus', () => this.handleInput())
    }

    setSuggestions(suggestions) {
        this.suggestions = suggestions || []
    }

    getCurrentToken() {
        const value = this.input.value
        const cursorPos = this.input.selectionStart
        const beforeCursor = value.substring(0, cursorPos)
        const lastSepIndex = beforeCursor.lastIndexOf(this.separator)
        const token = beforeCursor.substring(lastSepIndex + 1).trim()
        return { token, start: lastSepIndex + 1 }
    }

    handleInput() {
        const { token } = this.getCurrentToken()

        if (token.length === 0) {
            this.hideDropdown()
            return
        }

        const filtered = this.suggestions.filter(s =>
            s.toLowerCase().includes(token.toLowerCase())
        )

        if (filtered.length === 0) {
            this.hideDropdown()
            return
        }

        this.showDropdown(filtered)
    }

    showDropdown(items) {
        this.dropdown.innerHTML = items.map((item, idx) =>
            `<div class="autocomplete-item" data-index="${idx}">${item}</div>`
        ).join('')

        this.dropdown.classList.add('show')
        this.selectedIndex = -1

        // Add click handlers
        this.dropdown.querySelectorAll('.autocomplete-item').forEach(el => {
            el.addEventListener('click', () => this.selectItem(el.textContent))
        })
    }

    hideDropdown() {
        this.dropdown.classList.remove('show')
        this.selectedIndex = -1
    }

    selectItem(value) {
        const cursorPos = this.input.selectionStart
        const fullValue = this.input.value
        const beforeCursor = fullValue.substring(0, cursorPos)
        const afterCursor = fullValue.substring(cursorPos)

        const lastSepIndex = beforeCursor.lastIndexOf(this.separator)
        const beforeToken = fullValue.substring(0, lastSepIndex + 1)
        const afterToken = afterCursor.substring(afterCursor.indexOf(this.separator))

        // Build new value
        let newValue = beforeToken
        if (beforeToken.length > 0 && !beforeToken.endsWith(this.separator)) {
            newValue += this.separator + ' '
        } else if (beforeToken.length > 0) {
            newValue += ' '
        }
        newValue += value

        // Add separator and space if this is not the last item
        if (afterToken.length > 0) {
            newValue += afterToken
        } else {
            newValue += this.separator + ' '
        }

        this.input.value = newValue
        this.input.focus()

        // Set cursor after the inserted value
        const newCursorPos = newValue.length - afterToken.length
        this.input.setSelectionRange(newCursorPos, newCursorPos)

        this.hideDropdown()
    }

    handleKeydown(e) {
        if (!this.dropdown.classList.contains('show')) return

        const items = this.dropdown.querySelectorAll('.autocomplete-item')

        if (e.key === 'ArrowDown') {
            e.preventDefault()
            this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1)
            this.updateSelection(items)
        } else if (e.key === 'ArrowUp') {
            e.preventDefault()
            this.selectedIndex = Math.max(this.selectedIndex - 1, -1)
            this.updateSelection(items)
        } else if (e.key === 'Enter') {
            e.preventDefault()
            if (this.selectedIndex >= 0 && items[this.selectedIndex]) {
                this.selectItem(items[this.selectedIndex].textContent)
            }
        } else if (e.key === 'Escape') {
            this.hideDropdown()
        }
    }

    updateSelection(items) {
        items.forEach((item, idx) => {
            if (idx === this.selectedIndex) {
                item.classList.add('selected')
                item.scrollIntoView({ block: 'nearest' })
            } else {
                item.classList.remove('selected')
            }
        })
    }
}

// Export for use in admin.js
window.MultiAutocomplete = MultiAutocomplete
