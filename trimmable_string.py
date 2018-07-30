class TrimmableString:
    def __init__(self, string):
        self.string = string
        self.end = len(string)
    
    def __str__(self):
        return self.string[:self.end]

    def __repr__(self):
        return self.string[:self.end]

    def remove_word(self):
        substring = self.string[:self.end]
        
        space_loc = substring.rfind(' ', 0, self.end)
        if space_loc == -1:
            if substring == self.string:
                self.end = len(self.string)
            else:
                pass
        else:
            self.end = space_loc

        return self.string[:self.end]

    def remove_char(self):
        if self.end <= 1:
            return self.string[:self.end]

        self.end -= 1
        return self.string[:self.end]
    
    def reveal_word(self):
        if self.end == len(self.string):
            self.string[:self.end]
        
        space_loc = self.string.find(' ', self.end + 1)
        if space_loc == -1:
            self.end = len(self.string)
        else:
            self.end = space_loc

        return self.string[:self.end]

    def reveal_char(self):
        if self.end == len(self.string):
            return self.string[:self.end]

        self.end += 1
        return self.string[:self.end]