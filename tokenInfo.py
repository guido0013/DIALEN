import os
import re
        
#f = "book-nlp/data/tokens/dickens.oliver.tokens"
f = "book-nlp/data/tokens/austen.sense.tokens"
#f = "book-nlp/data/tokens/austen.pride.tokens"
        
class TokenInfo:

    def __init__(self, f):
        #self.d_qt = ['\"', '“', '”']
        #self.s_qt = ['\'', '‘', '’']
        self.all_qt = ['\"', '\'', '“', '”', '‘', '’']
    
        self.tks_info, self.paragraphs = self.extract(f)
        self.isDouble, self.qt_marks = self.decide_quoting()
        self.add_quotations()
        
    
    def extract(self, f):
        with open(f, 'r') as tks:
            paragraphs = {}
            
            s = []
            prev_id = 0
            
            tks_info = {} # list of info per feature
            next(tks)
            for line in tks:
                line = re.sub("\n$", "", line)
                l = line.split('\t')
                
                p_id = int(l[0])
                t_id = int(l[2])
                tk = l[7]
                tks_info[t_id] = l
                
                if not p_id in paragraphs.keys():
                    paragraphs[p_id] = []
                
                paragraphs[p_id].append(t_id)
        return tks_info, paragraphs
    
    
    def get_paragraph(self, p_id):
        return self.paragraphs[p_id]
        
    def print_words(self, p_id):
        snt = [self.word(t_id) for t_id in self.paragraphs[p_id]]
        print(" ".join(snt))
        
    def separation(self, t_id):
        return self.tks_info[t_id][5]
    
    def dependency(self, t_id):
        return int(self.tks_info[t_id][6]) 
        
    def word(self, t_id):
        return self.tks_info[t_id][7]
        
    def pos(self, t_id):
        return self.tks_info[t_id][10]
    
    def ner(self, t_id):
        return self.tks_info[t_id][11]
    
    def dependency_label(self, t_id):
        return self.tks_info[t_id][12]
        
    def quotation(self, t_id):
        return self.tks_info[t_id][13]
        
    def add_quotation(self, t_id, isQuotation):
        self.tks_info[t_id][13] = isQuotation
        
    def char_id(self, t_id):
        return int(self.tks_info[t_id][14])
        
    def add_char_id(self, t_id, char_id):
        self.tks_info[t_id][14] = char_id


    def decide_quoting(self):
        # decide way of quoting by counting total quotation marks of each type
        d_qt = ['\"', '“', '”']
        s_qt = ['\'', '‘', '’']
        
        c_d = 0
        c_s = 0
        for p in self.paragraphs:
            for t_id in self.paragraphs[p]:
                word = self.word(t_id)
                if word in d_qt:
                    c_d += 1
                elif word in s_qt:
                    c_s += 1
                    
        if c_d > c_s:
            isDouble = True
            qt_marks = d_qt
        else:
            isDouble = False
            qt_marks = s_qt
        
        return isDouble, qt_marks
     
     
    def write_to_file(self, fn):
        with open(fn, 'w') as tks:    
            for i in range(0, len(self.tks_info)):
                tks.write("\t".join(str(x) for x in self.tks_info[i]) + "\n")    
        
    def add_quotations(self):
        punct = [',','.',':']
            
        for p_id in self.paragraphs.keys():
            count = 0
            
            words = self.paragraphs[p_id] 
        
            for tkn in words:
            
                if self.word(tkn) in self.qt_marks:
                    # Ignore possessive quotation marks
                    if self.pos(tkn) != "POS":
                        count += 1
                        self.add_quotation(tkn, "quotation")
                    else:
                        self.add_quotation(tkn, "false")
                else: 
                    self.add_quotation(tkn, "false")
            
    
            # If there are no quotation marks in a paragraph, there is nothing to do
            if count == 0:
                pass
                
                
            # If there is only one quotation mark, it cannot be part of direct speech, so change the one mark back to 
            #false (Or there is an annotation error, in which case it will be hard to detect where there is one missing)        
            elif count == 1:
                for tkn in words:
                    if self.word(tkn) in self.all_qt:
                        self.add_quotation(tkn, "false")           
            
            
            elif count == 2:
                    
                # Find first and last instance of quotation mark
                first_i = next((tkn for tkn in words if self.quotation(tkn) == "quotation"))
                last_i = next((tkn for tkn in list(reversed(words)) if self.quotation(tkn) == "quotation"))
                
                if self.isDouble:
                    # check whether previous token is a quotation mark
                    if self.pos(last_i - 1) in self.all_qt:
                        prev_tk = last_i - 2
                    else: 
                        prev_tk = last_i - 1
                   
                   
                    # in principle the token before last qt mark should be a punctuation symbol, this is to filter out
                    # other types of phrases between punctuation marks
                    if self.pos(prev_tk) in punct: 
                            
                        for tkn in words:
                                    
                            if tkn < first_i or tkn > last_i:
                                self.add_quotation(tkn, "false")
                            else:
                                self.add_quotation(tkn, "true")  
                 
                    else:
                        for tkn in words:
                            self.add_quotation(tkn, "false")  
                                                     
                else:
                
                    for tkn in words:       
                        if tkn < first_i or tkn > last_i:
                            self.add_quotation(tkn, "false")
                        else:
                            self.add_quotation(tkn, "true")  
                
                
            elif count == 3: #TODO: look at tks_info for ""' in pride & prejudice
                if not self.isDouble:
                    # Find first and last instance of quotation mark
                    first_i = next((t_id for t_id in words if self.quotation(t_id) == "quotation"))
                    offset = first_i - words[0]
                    middle_i = next((t_id for t_id in words[offset:] if self.quotation(t_id) == "quotation"))
                    last_i = next((t_id for t_id in list(reversed(words)) if self.quotation(t_id) == "quotation"))
                    
                    
                    if self.pos(middle_i - 1) in self.all_qt:
                        m_prev_tk = middle_i - 2
                    else: 
                        m_prev_tk = middle_i - 1
                        
                        
                    if self.pos(last_i - 1) in self.all_qt:
                        l_prev_tk = last_i - 2
                    else: 
                        l_prev_tk = last_i - 1
                    
                    # if first word is quotation mark and last word is a quotation mark preceded by a punctuation symbol ->
                    # it is quite likely that those two are direct speech
                    if first_i == words[0] and self.pos(l_prev_tk) in punct:
                        for t_id in words:
                                    
                            if t_id < first_i or t_id > last_i:
                                self.add_quotation(t_id, "false")
                            else:
                                self.add_quotation(t_id, "false")           
                    
                    # Next most likely senario is that the middle is quotation mark preceded by a punctuation symbol 
                    elif first_i == words[0] and self.pos(m_prev_tk) in punct:
                        for t_id in words:
                                    
                            if t_id < first_i or t_id > middle_i:
                                self.add_quotation(t_id, "false")
                            else:
                                self.add_quotation(t_id, "true")
                         
                    # If not one of those senarios, there is probably an annotation/tokenization error, making it difficult
                    # to decide correct way of handling paragraph -> ignore it (for now)
                    else:
                        for t_id in words:
                            self.add_quotation(t_id, "false")  
                            
                            
                # in case of double quotation marks, it is almost always either an annotation/tokenization error or 
                # a letter            
                else:
                        for t_id in words:
                            self.add_quotation(t_id, "false")  
               
            # in case of even number of quotes, also have limit on number of quotation marks as more prob violates one
            # speaker per paragraph 
            elif count % 2 == 0 and count < 9:
                quotes = [t_id for t_id in words if self.quotation(t_id) == "quotation"]
                total = len(quotes)
                
                #only if single quotes (double quotes almost always mean direct speech), remove all quotation symbols
                # not preceded by punctuation symbol
                if not self.isDouble:
                        
                    #check previous symbol
                    for q_i in quotes:
                    
                        if self.pos(q_i - 1) in self.all_qt:
                            prev_tk = q_i - 2
                        else: 
                            prev_tk = q_i - 1
                        
                        if q_i == words[0] or self.pos(prev_tk) in punct:
                            pass
                        else:
                            quotes.remove(q_i)
                            
                            
                # In case we still have an even number of quotation symbols, handle them regularly
                if len(quotes) % 2 == 0:
                    mark_as = False
                    
                    for t_id in words:
                        last_qt = False
                        if t_id in quotes and mark_as == False:
                            mark_as = True
                        elif t_id in quotes and mark_as == True:
                            mark_as = False
                            last_qt = True
                            
                        if mark_as == True or last_qt:
                            self.add_quotation(t_id, "true")
                        else:
                            self.add_quotation(t_id, "false")
            else:
                for t_id in words:
                    self.add_quotation(t_id, "false")
                    
     
     
class CharacterInfo:

    def __init__(self, tks):
        self.aliases = {}
        self.pronouns = self.aliases_list(tks)
        self.genders = self.gender_classifier(tks)
        
    # Get list of characters with aliases, ignore PRP, only look at NNP
    def aliases_list(self, tks):
        pronouns = {} # list of pronouns used, for that person (for gender identification)
        skip_some = 0
        for t_id in range(0, len(tks.tks_info)):
            # don't loop and include parts of aliases already dealt with
            if skip_some > t_id:
                continue
            
            char_i = tks.char_id(t_id)
            if char_i != -1:
            
                # If the index is a pronoun, add it to pronoun list 
                if tks.pos(t_id) ==  "PRP$" or tks.pos(t_id) == "PRP":
                    prp = tks.word(t_id).lower()
                    
                    if char_i in pronouns.keys():
                        if not prp in pronouns[char_i].keys():
                            pronouns[char_i][prp] = 1
                        else:
                            pronouns[char_i][prp] += 1
                    else:
                        pronouns[char_i] = {prp: 1}
                      
                else:
                
                    new_char_i = char_i
                    j = 1
                    alias = ""
                    
                    while char_i == new_char_i:
                        alias += " " + tks.word(t_id + j - 1)
                        try: # avoid j becoming out of bounce
                            new_char_i = tks.char_id(t_id + j)
                        except KeyError:
                            new_char_i = -1
                        j += 1
                        
                    alias = re.sub("^\s", "", alias) # remove initial space
                    skip_some = t_id + j - 1

                    if char_i in self.aliases.keys():
                        self.add_alias(char_i, alias)
                            
                    else:
                        self.add_char(char_i, alias)
            
        return pronouns  
       
       
    def get_aliases(self, char_id):
        if char_id in self.aliases.keys():
            return list(self.aliases[char_id].keys())
        else:
            return []
    
    def get_name(self, char_id):
        if char_id in self.aliases.keys():
            # return the name that has most occurrences
            v = list(self.aliases[char_id].values())
            k = list(self.aliases[char_id].keys())
            
            return k[v.index(max(v))]
        else:
            return "unknown"
 
    def get_char_ids(self):
        return list(self.aliases.keys())
        
    def get_chars(self):
        return [self.get_name(char_id) for char_id in self.get_char_ids()]
        
    def get_char_freq(self, char_id):
        if char_id in self.aliases.keys():
            return sum(self.aliases[char_id].values())
        else:
            return 0
    
    def add_alias(self, char_id, alias):
        if not alias in self.aliases[char_id]:
            self.aliases[char_id][alias] = 1
        else:
            self.aliases[char_id][alias] += 1
    
    def add_char(self, alias):
        new_char_id = len(self.aliases)
        self.add_char(new_char_id, alias) 
    
    def add_char(self, char_id, alias):
        self.aliases[char_id] = {alias: 1} 


    def unify_chars(self, char_id1, char_id2):
        for alias in self.aliases[char_id2]:
            count = self.aliases[char_id2][alias]
            if alias in self.aliases[char_id1]:
                self.aliases[char_id1][alias] += count
            else:
                self.aliases[char_id1][alias] = count
        self.aliases.pop(char_id2)
            

    def gender_classifier(self, tks):
        genders = {}
        
        male_pronouns = set(["he","his","him","himself"])
        female_pronouns = set(["she","her","herself"])
        male_indications = set(["mr","sir","mr.", "mister"])
        female_indications = set(["mrs","madame","miss","lady", "mrs.", "ms.","ms","missis", "missus"])
        
        for i in self.aliases:
            gender = "u" # u for unknown/undecided
            m_ind = False
            f_ind = False
            m = 0
            f = 0
        
            for a in self.get_aliases(i):
                alias = a.split()
                for word in alias:
                    if word.lower() in male_indications:
                        m_ind = True
                    elif word.lower() in female_indications: 
                        f_ind = True
              
            if m_ind and not f_ind:
                gender = "m"
            elif f_ind and not m_ind:
                gender = "f"
            else: # continue with pronoun ratios
                if i in self.pronouns.keys():
                    for prp in self.pronouns[i].keys():
                        if prp in male_pronouns:
                            m += self.pronouns[i][prp]
                        elif prp in female_pronouns:
                            f += self.pronouns[i][prp]
                if m > f:
                    gender = "m"
                elif f > m:
                    gender = "f"        
        
            genders[i] = gender
            
        return genders


    def get_gender(self, char_id):
        return self.genders[char_id]              
      
      
      
      
class SpeakerUtteranceAttribution:

    def __init__(self, tks, chars): 
        self.tks = tks
        self.chars = chars
        self.narrative_words = set(["hissed","declared","repeated","said","asked","replied","answered","cried",
"responded", "added","screamed","wondered", "reflected","pondered","ejaculated","rejoined","inquired", "says", 
"announced", "offered", "began","continued", "mumbled","whispered","roared", "retorted", "sneered", "resumed", "added", 
"observed", "returned", "interposed", "stammered", "affirmed", "confirmed", "denied", "exclaimed", "interrupted",
"pursued", "sobbed", "blubbered", "urged", "growled", "demanded", "remonstrated", "muttered", "murmured", "reasoned",
"remarked", "acquiesced", "echoed", "croaked", "renewed", "bawled", "thundered", "submitted", "gasped", "laughed",
"suggested", "faltered","thought", "conjectured"])
    
        self.turn_distance = 2 # Distance to decide on whether current quote is part of previous dialogue
        self.dialogues = {} # list of p_ids for each dialogue (each dialogue has a unique id)
        self.dialogue_participants = {} # participants in dialogue (d_id = key) -> Dictionary of participants with t_ids as values
        self.paragraphs_info = {} # indexed by p_id. Values are lists: [speaker_id, alias_used, currentTurn, prevTurn,
                                  # QuoteSnt, NarrativeWord, [adverbsOutsideQuote], [adjectivesInsideQuotes]]
    
        self.speaker_utterance_attribution()

        
    def speaker_utterance_attribution(self):
        
        self.first_pass()
        self.second_pass()
        self.third_pass()
 

########################################################################################################################
########################################### First Pass ################################################################# 
########################################################################################################################      
      
        
    # First pass through paragraphs. Detects:
    # - speakers, based on a narrative word:
    #   - nsubj dependency of the narrative word is captured
    #   - An NE in a limited window around the narrative word
    #   - Quote - narrative word - mention - pattern, where the mention is captured 
    # - Dialogue boundaries of max distance 3
    def first_pass(self):
        punct = set(['.', ':', ','])
        verbs = set(["VBG", "VB", "VBD", "VBN", "VBP", "VBZ"])
        preps = set(["IN", "TO"])
        
        narrative_i = 3 # check on i-3,...,i+3 if contains a name
    
        for p_id in self.tks.paragraphs:
            quote = [] # current quote
            onlyQuote = False # True if whole paragraph is quote
            speaker = [] # 1st element = char_id, then series of t_ids
            narrative_used = False # check if a narrative word is used
            narrative_word = "none"
            adverbs = set()
            adjectives = set()
            rule = "none"
            
            
            for t_id in self.tks.paragraphs[p_id]:
                   
                if self.tks.quotation(t_id) == "true":
                    quote.append(t_id)
                 
                #TODO: classify narrative word 
                # If there is a narrative word 
                elif self.tks.word(t_id).lower() in self.narrative_words:
                    narrative_used = True
                    narrative_word = self.tks.word(t_id).lower()
                    
                    speaker, rule = self.find_speaker(p_id, t_id, speaker, rule, narrative_i, punct, verbs)

                # Adverbs outside quotation
                elif self.tks.pos(t_id) == "RB":
                    adverbs.add(self.tks.word(t_id).lower())
                    
                # Adjectives outside quotation
                elif self.tks.pos(t_id) == "JJ":
                    adjectives.add(self.tks.word(t_id).lower())
                    
                
            if quote == self.tks.paragraphs[p_id]:
                onlyQuote = True 
            
            # After processing the quotation/speakers/adverbs/adjectives etc. Decide on dialogue turn info, etc
            
            current_turn = self.decide_turn(quote, p_id)
            
            
            # if finished a dialogue, look at the previous dialogue to unify participants
            if current_turn == 1:
                # if there is at least a previous dialogue
                prev_dialogue = len(self.dialogues) - 1
                if prev_dialogue != -1:
                    self.unify_participants(prev_dialogue)
            
            
            # add dialogue info (speaker, participants, divide in dialogues)
            self.add_dialogue_info(quote, p_id, current_turn, speaker)
                
            snt = self.pretty_quote(quote, tks)
            
            #[1] = list of mentions
            self.paragraphs_info[p_id] = [speaker, [], current_turn, snt, onlyQuote, narrative_word, adverbs, adjectives, rule]     
       
       
      
    # Find a speaker, based on the detection of a narrative word   
    def find_speaker(self, p_id, t_id, speaker, rule, narrative_i, punct, verbs):
        
        # First check if there is an nsubj of narrative word
        for entity_t in self.tks.paragraphs[p_id]:
            if self.tks.dependency_label(entity_t) == "nsubj" and t_id == self.tks.dependency(entity_t):
                # If NE, collect whole name
                if self.tks.quotation(entity_t) == "false":
                    if self.tks.char_id(entity_t) != -1:
                        speaker = self.whole_ne(entity_t)
                        rule = "nsubj"
                    # If not, collect dependencies of word  
                    #else:
                    #    self.tks.print_words(p_id)
                        #speaker = self.whole_dep(entity_t)
                        #print(" ".join([self.tks.word(s) for s in speaker[1:]]))
                
                        
        # If no speaker has been found yet, try to find speaker outside of nsubj and close to narrative word      
        if speaker == []:    
            # first check if followed or preceded by tagged name (alias)
            possible_speaker = -1
            for i in range(t_id - narrative_i, t_id + narrative_i + 1): 
                if self.tks.quotation(i) == "false":
                    possible_speaker = self.tks.char_id(i)
                if possible_speaker != -1: # if speaker has been found -> stop
                    speaker = self.whole_ne(i)
                    rule = "limited"
                    break
                
        # If not preceded by NE, check if narrative word follows pattern, if so take all that comes after 
        # until punct
        #TODO: Use dep labels and POS to decide name
        if speaker == []:
            if self.tks.pos(t_id - 2) in punct and self.tks.pos(t_id - 1) == "''":
            
                next_id = t_id + 1
                alias = []
                char_id = self.find_next_id()
                speaker.append(char_id)
                speaker_t_ids = []
                contains_adverb = -2 # to check for unwanted adverbs
                
                while self.tks.pos(next_id) not in punct and self.tks.word(next_id) not in self.tks.all_qt:
                    alias.append(self.tks.word(next_id))
                    speaker.append(next_id) 
                    self.tks.add_char_id(next_id, char_id)
                    speaker_t_ids.append(next_id)
                    if self.tks.pos(next_id) == "RB":
                        contains_adverb = next_id
                    next_id += 1
                rule = "narr_pat"
                    
                #TODO: Check if name contains adverbs and remove them if there is no verb/prep
                pos_tags = set(self.tks.pos(speaker_t_id) for speaker_t_id in speaker_t_ids)
                if contains_adverb != -2 and verbs.isdisjoint(pos_tags):
                    self.tks.add_char_id(contains_adverb, -1)
                    speaker.remove(contains_adverb)
                    alias.remove(self.tks.word(contains_adverb))
                #print(" ".join([self.tks.word(tt) for tt in speaker[1:]]))
                self.chars.add_char(char_id, " ".join(alias))   
        
        
        return speaker, rule


    def whole_ne(self, t_id): 
        char_id = self.tks.char_id(t_id)
        speaker = [char_id] 
        
        # complete NE alias by looking at if previous and next tokens are part of same NE
        i_min = t_id - 1
        while self.tks.char_id(i_min) == char_id and self.tks.quotation(i_min) == "false" and i_min != -1: 
            speaker.append(i_min)
            i_min -= 1
            
        speaker.append(t_id)
        i_plus = t_id + 1    
        while self.tks.char_id(i_plus) == char_id and self.tks.quotation(i_plus) == "false" and i_plus != len(self.tks.tks_info):
            speaker.append(i_plus)
            i_plus += 1  
                
        return speaker
        
        
    def whole_dep(self, t_id):
        char_id = self.tks.char_id(t_id)
        speaker = [char_id] 
        
        # Look in context of sentence (= without crossing punctuation or quoted speech.)
        # Document all dependencies -> remove the ones not attached to nsubj
        
        # complete NE alias by looking at if previous and next tokens are part of same NE
        i_min = t_id - 1
        while self.tks.char_id(i_min) == char_id and self.tks.quotation(i_min) == "false" and i_min != -1: 
            speaker.append(i_min)
            i_min -= 1
            
        speaker.append(t_id)
        i_plus = t_id + 1    
        while self.tks.char_id(i_plus) == char_id and self.tks.quotation(i_plus) == "false" and i_plus != len(self.tks.tks_info):
            speaker.append(i_plus)
            i_plus += 1  
                
        return speaker
        
    
    def find_next_id(self):
        char_id_list = sorted(self.chars.aliases.keys())
        for i in range(0, len(char_id_list) + 1):
            if i not in char_id_list:
                #print(i)
                return i


    def decide_turn(self, quote, p_id):
        if quote != []:
            prev_turn = 0
            for i in reversed(range(p_id - self.turn_distance, p_id)):
                if i in self.paragraphs_info.keys():
                    if self.current_turn(i) != 0:
                        prev_turn = self.current_turn(i)  
                        break
            
            current_turn = prev_turn + 1
            
        else:
            current_turn = 0
        
        return current_turn


    def unify_participants(self, d_id):
        # some tricks to unify participants:
        # looking at removing adjectives/adverbs and see if it matches a participant
        # v If same name
        # v Ignore capitalization differences
        # See if participant matches other with or without Mr/Ms etc
        participants = self.dialogue_participants[d_id]
        
        removed = []
        
        for char_id in participants.keys():
            if char_id not in removed:
                # make sure we only look at the NE's that were not tagged as NE
                if self.chars.get_char_freq(char_id) == 1 and char_id != -1: 
                    #print(self.chars.get_name(char_id) + " --- " + str(d_id))
                    # Check if this participant matches any other participant
                    for char_j in participants.keys():
                        if char_j not in [i[1] for i in removed] and char_j != char_id and char_j != -1:
                            if self.unifying_criteria(d_id, char_id, char_j):
                                #print(self.chars.get_name(char_id) + " (" + str(char_id) + ")" + " - " + self.chars.get_name(char_j) + " (" + str(char_j) + ")")
                                self.chars.unify_chars(char_id, char_j)
                                removed.append((char_id, char_j))
    
    
        # Update tks_info and dialogue participants, the speakers (so that speakers get right id) and tks_info
        for (char_to, char_from) in removed:
            #print(str(char_to) + "----" + str(char_from))
            # update tksinfo and dialogue participants
            updated_chars = self.dialogue_participants[d_id][char_from]

            # update tksinfo:
            for full_char in updated_chars:
                for t_id in full_char:
                    self.tks.add_char_id(t_id, char_to)
            
            # update dialogue_participants 
            self.dialogue_participants[d_id][char_to].extend(updated_chars)
            self.dialogue_participants[d_id].pop(char_from)
            
            # update speaker
            for p_id in self.dialogues[d_id]:
                if self.speaker(p_id) != []:
                    if self.speaker(p_id)[0] == char_from:
                        self.speaker(p_id)[0] = char_to
    
    
    #TODO: Look at all names, instead of most common (dialogue_participants)
    def unifying_criteria(self, d_id, char_1, char_2):
        verbs = set(["VBG", "VB", "VBD", "VBN", "VBP", "VBZ"])
        preps = set(["IN", "TO"])
    
        aliases1 = self.chars.get_aliases(char_1)
        aliases2 = self.chars.get_aliases(char_2)  
        #print(str(aliases1) + " ----- " + str(aliases2))
        
        same = False
        name = self.chars.get_name(char_1)
        other_name = self.chars.get_name(char_2)
        if name.lower() == other_name.lower():
            return True  
            
        # Check if name matches other name without adverb 
        full_names = self.dialogue_participants[d_id].get(char_1)
        for char in full_names:
            for t_id in char:
                #if self.tks.pos(t_id) == "JJ":
                #if self.tks.word(t_id) in set(["mr","sir","mr.", "mister", "mrs","madame","miss", "mrs.", "ms.","ms","missis", "missus"]):
                    #pos_tags = set(self.tks.pos(c) for c in char)
                    #TODO: Check for name matching with omitting adverbs and adjectives
                    #TODO: Check for name matching with omitting Mr etc
                    # In this case, there is an adverb that is referrring to the way the utterance is uttered
                    #if not verbs.isdisjoint(pos_tags):
                   #print(" ".join([self.tks.word(c) for c in char]))
                pass    
                        
        return same
  

    def add_dialogue_info(self, quote, p_id, current_turn, speaker):
        if quote != []:
            # if new dialogue -> start new list of paragraphs
            if current_turn == 1:
                new_id = len(self.dialogues)
                self.dialogues[new_id] = [p_id]
                self.dialogue_participants[new_id] = {}
            else:
                self.dialogues[len(self.dialogues) - 1].append(p_id)
                
            # add dialogue speakers info                      
            if speaker != []:
                if speaker[0] in self.dialogue_participants[len(self.dialogues) - 1]:
                    self.dialogue_participants[len(self.dialogues) - 1][speaker[0]].append(speaker[1:]) 
                else:
                    self.dialogue_participants[len(self.dialogues) - 1][speaker[0]] = [speaker[1:]]
            else:
                self.dialogue_participants[len(self.dialogues) - 1][-1] = []    
                   
                    

########################################################################################################################
########################################### Second Pass ################################################################ 
########################################################################################################################

    #TODO: Unify dialogues within a fixed range with overlap in speakers
    #TODO: Refine dialogue boundaries
    #TODO: Unify speakers within dialogues
    #TODO: Don't consider speakers that mention their full name in quote (some
    # Detects:
    # - Speakers based on:
    #   - Vocative pattern
    #   - Single mention in paragraph 
    #   - Conversational pattern
    def second_pass(self):
        
        for d_id in self.dialogues:
            participants = self.dialogue_participants[d_id]
            
            # all names used for the current participants in the dialogue. This might help in finding untagged mentions
            # reasoning is that relevant mentions are already part of the current dialogue and not having this
            # restriction might result in too many mentions
            all_aliases = {}
            for p in participants.keys():
                for alias in self.chars.get_aliases(p):
                    all_aliases[alias] = p
                    
            
            for p_id in self.dialogues[d_id]:
                # Find all mentions
                mentions = self.find_all_mentions(all_aliases, p_id)
                
                 
                #### Add new speakers if missing
                if self.speaker(p_id) == []:
                    
                    # single mention in paragraph
                    chars_outside = []
                    for mention in mentions:
                        # mention is in non-quote text
                        if mention[1] == False:
                            chars_outside.append([mention[0], mention[3]])
                    # if only 1 single mention
                    if len(chars_outside) == 1:
                        self.add_speaker(d_id, p_id, chars_outside[0][0], [chars_outside[0][1]])
                        self.add_detected_pattern(p_id, "single_mnt")

                if self.speaker(p_id) == []:
                    # vocative pattern
                    current_turn = self.current_turn(p_id)
                    # index -1 to access right p_id in list of dialogue p_ids
                    if current_turn != 1:
                    
                        pid_index = self.dialogues[d_id].index(p_id)
                        prev_pid = self.dialogues[d_id][pid_index - 1]
                        
                        voc_mentions = self.containsVocative(prev_pid)
                        
                        
                        if  voc_mentions != []:
                            self.find_voc_pattern_speaker(d_id, p_id, voc_mentions)
                                    
                        # if no voc_mentions, check if there is a conversational pattern 
                        elif(current_turn > 2 and # there should be 2 utterances before the current one
                             self.speaker(prev_pid) != [] and self.speaker(self.dialogues[d_id][pid_index - 2]) != []): # the previous 2 quotes must have a speaker
                            
                            pid_min2 = self.dialogues[d_id][pid_index - 2]
                            char_id1 = self.speaker(prev_pid)[0]
                            char_id2 = self.speaker(pid_min2)[0]
                            if(self.onlyQuote(p_id) and # the current utterance has to be a quote
                              self.speaker(p_id) == [] and # the current utterance doesn't already have a speaker
                              char_id1 != char_id2 and # the previous 2 speakers cannot be the same
                              prev_pid == p_id - 1 and pid_min2 == p_id - 2): # Only consider adjacent paragraphs with quotes
 
                                # Only add if, in case there is a next speaker, it is not the same as the current one
                                if(not(pid_index < len(self.dialogues[d_id]) - 1) or (self.speaker(self.dialogues[d_id][pid_index + 1]) != [] and self.speaker(self.dialogues[d_id][pid_index + 1])[0] != self.speaker(pid_min2)[0])):
                                    char_id = self.speaker(pid_min2)[0]
                                    t_ids = self.speaker(pid_min2)[1:]
                                    self.add_speaker(d_id, p_id, char_id, t_ids)
                                    self.add_detected_pattern(p_id, "strict_conv_pat1")
                                        
            
            
            if -1 in self.dialogue_participants[d_id]:
                n_prtpnts = 0
                for prtpnt in self.dialogue_participants[d_id]:
                    n_prtpnts += len(self.dialogue_participants[d_id][prtpnt])
                if len(self.dialogues[d_id]) == n_prtpnts:
                    self.dialogue_participants[d_id].pop(-1)  


    def find_all_mentions(self, all_aliases, p_id):
        mentions = [] # each mention = [char_id, isInsideQuote/vocative, [t_ids]]
        t_id = self.tks.paragraphs[p_id][0]
        
        while t_id in range(t_id, self.tks.paragraphs[p_id][-1] + 1):
            char_id = -1
            isInsideQuote = False
            isVocative = False
            t_ids = []
            
            # if we found a NE
            if self.tks.char_id(t_id) != -1:
                char_id = self.tks.char_id(t_id)
                    
                t_ids.append(t_id)
                i = t_id + 1    
                
                while self.tks.char_id(i) == char_id and i != len(self.tks.tks_info):
                    t_ids.append(i)
                    i += 1
                
                # check if vocative and within quotation
                if self.tks.quotation(t_ids[0]) == "true":
                    isInsideQuote = True
                isVocative = self.isVocative(p_id, t_ids)
                
                # get offset right    
                t_id = i - 1
                
            else:
                for alias in all_aliases.keys():
                    if self.tks.word(t_id) == alias.split()[0]:
                        all_ids = list(range(t_id, t_id + len(alias.split()), 1))
                        if [self.tks.word(t_id) for t_id in all_ids] == alias.split():
                            #update tks info
                            for t_id in all_ids:
                                self.tks.add_char_id(t_id, all_aliases[alias])  
                            # update mentions info
                            t_ids = all_ids
                            if self.tks.quotation(t_ids[0]) == "true":
                                isInsideQuote = True
                            isVocative = self.isVocative(p_id, t_ids)
                            char_id = all_aliases[alias]
                            
                            
            # update t_id
            t_id += 1
            
            # update mentions
            if t_ids != []:
                mentions.append([char_id, isInsideQuote, isVocative, t_ids])
                
                
        # add mentions to paragraphs_info
        self.paragraphs_info[p_id][1] = mentions

        return mentions


    # check on a vocative patterns. Patterns taken from (Muzny et al., 2017)
    def isVocative(self, p_id, t_ids):
        # check if t_id matches pattern in paragraph
        #check whether what is between is a char (using dialogue participants)
        beginning_voc = self.tks.word(t_ids[0] - 1)
        ending_voc = self.tks.word(t_ids[-1] + 1)
        
        if beginning_voc == ",":
            if(ending_voc == "!" or 
               ending_voc == "?" or 
               ending_voc == "." or 
               ending_voc == '"' or 
               ending_voc == ";" or 
               ending_voc == "," or 
               ending_voc == "'"):
                return True
        if (beginning_voc == "'" or beginning_voc == '"') and ending_voc == ",":
                return True       
        if beginning_voc.lower() == "dear":
            return True
        if beginning_voc.lower() == "oh" and ending_voc == "!":
            return True
            
        
        return False


    def find_voc_pattern_speaker(self, d_id, p_id, voc_mentions):
        if len(voc_mentions) == 1:
            mention = voc_mentions[0]
            self.add_speaker(d_id, p_id, mention[0], [mention[3]])
            self.add_detected_pattern(p_id, "single_voc")
        
        # if more than one vocative pattern, look if all mentions have same char_id, if not ignore the vocative pattern
        else:
            
            voc_speakers = set(mention[0] for mention in voc_mentions)
            if len(voc_speakers) == 1:
                char_id = list(voc_speakers)[0]
                t_ids = next(mention[3] for mention in voc_mentions if mention[0] == char_id)
                self.add_speaker(d_id, p_id, char_id, t_ids)
                self.add_detected_pattern(p_id, "multiple_voc")
            # if there are more voc_speakers -> check if only one of them is in dialogue participants
            else:
                pass        
     
                
    def containsVocative(self, p_id):
        vocative_mentions = [] 
        for mention in self.mentions(p_id):
            if mention[2]:
                vocative_mentions.append(mention)
        return vocative_mentions    



########################################################################################################################
########################################### Third Pass ################################################################# 
########################################################################################################################
    
    
    #TODO: Make final dialogue boundary decisions
    #TODO: Fill in unknown speakers based on loose conversational patterns
    #TODO: Paragraph Final Mention Linking

    # Detect speakers based on:
    # - new combined dialogues and hence possibility of new vocative patterns
    # - More loose conversational patterns
    # - Majority speaker in dialogue or in text
    def third_pass(self):
    
        # Create a list of all aliases in the book
        #new_aliases = {}
        #for d_id in self.dialogues:
        #    participants = self.dialogue_participants[d_id]
        #    for p in participants.keys():
        #        for alias in self.chars.get_aliases(p):
        #            new_aliases[alias] = p
    
    
        for d_id in self.dialogues:
                    
            
            #for p_id in self.dialogues[d_id]:
                # Find all mentions
            #    mentions = self.find_voc_mentions(new_aliases, p_id)
        
            for p_id in self.dialogues[d_id]:
                if self.speaker(p_id) == []:
                    # vocative pattern
                    current_turn = self.current_turn(p_id)
                    # index -1 to access right p_id in list of dialogue p_ids
                    if current_turn != 1:
                    
                        pid_index = self.dialogues[d_id].index(p_id)
                        prev_pid = self.dialogues[d_id][pid_index - 1]
                        
                        voc_mentions = self.containsVocative(prev_pid)  
                        
                        if  voc_mentions != []:
                            self.find_voc_pattern_speaker(d_id, p_id, voc_mentions)
                            self.add_detected_pattern(p_id, "new_vocs")
                                    
                        # if no voc_mentions, check if there is a conversational pattern 
                        elif(current_turn > 2 and # there should be 2 utterances before the current one
                             self.speaker(prev_pid) != [] and self.speaker(self.dialogues[d_id][pid_index - 2]) != []): # the previous 2 quotes must have a speaker
                            
                            pid_min2 = self.dialogues[d_id][pid_index - 2]
                            char_id1 = self.speaker(prev_pid)[0]
                            char_id2 = self.speaker(pid_min2)[0]
                            
                            if(self.onlyQuote(p_id) and # the current utterance has to be onlyQuote
                              self.speaker(p_id) == [] and # the current utterance doesn't already have a speaker
                              char_id1 != char_id2 and # the previous 2 speakers cannot be the same
                              prev_pid == p_id - 1 and pid_min2 == p_id - 2): # Only consider adjacent paragraphs with quotes

                                if(not(pid_index < len(self.dialogues[d_id]) - 1) or (self.speaker(self.dialogues[d_id][pid_index + 1]) != [] and self.speaker(self.dialogues[d_id][pid_index + 1])[0] != self.speaker(pid_min2)[0])): # if there is a next speaker
                                    char_id = self.speaker(pid_min2)[0]
                                    t_ids = self.speaker(pid_min2)[1:]
                                    self.add_speaker(d_id, p_id, char_id, t_ids)
                                    self.add_detected_pattern(p_id, "strict_conv_pat2")
                                    
                                elif(pid_index < len(self.dialogues[d_id]) - 1 and self.speaker(self.dialogues[d_id][pid_index + 1]) == []):
                                    char_id = self.speaker(pid_min2)[0]
                                    t_ids = self.speaker(pid_min2)[1:]
                                    self.add_speaker(d_id, p_id, char_id, t_ids)
                                    self.add_detected_pattern(p_id, "strict_conv_pat3")
                                    
                        
                        # If that fails because the paragraph "in between" doesn't have a speaker, allow the pattern     
                        elif(current_turn > 2 and self.speaker(self.dialogues[d_id][pid_index - 2]) != []): # the n-2 utterance must have a speaker
                            pid_min2 = self.dialogues[d_id][pid_index - 2]
                            char_id2 = self.speaker(pid_min2)[0]
                            
                            if(self.onlyQuote(p_id) and # the current utterance has to be onlyQuote
                               prev_pid == p_id - 1 and pid_min2 == p_id - 2): # Only consider adjacent paragraphs with quotes

                                if(not(pid_index < len(self.dialogues[d_id]) - 1) or (self.speaker(self.dialogues[d_id][pid_index + 1]) != [] and self.speaker(self.dialogues[d_id][pid_index + 1])[0] != self.speaker(pid_min2)[0])): # if there is a next speaker that is not the same as the n-2 speaker
                                    char_id = self.speaker(pid_min2)[0]
                                    t_ids = self.speaker(pid_min2)[1:]
                                    self.add_speaker(d_id, p_id, char_id, t_ids)
                                    self.add_detected_pattern(p_id, "gap_conv_pat")
                
                # Try to nail down a speaker, based on simple heuristics            
                if self.speaker(p_id) == []:
                    self.find_speaker_heuristics(d_id, p_id)


                # if all else failed to find a speaker, assign the majority speaker in the dialogue to utterance
                if self.speaker(p_id) == []:
                    self.find_majority_speaker(d_id, p_id)
               
            if -1 in self.dialogue_participants[d_id]:
                n_prtpnts = 0
                for prtpnt in self.dialogue_participants[d_id]:
                    n_prtpnts += len(self.dialogue_participants[d_id][prtpnt])
                if len(self.dialogues[d_id]) == n_prtpnts:
                    self.dialogue_participants[d_id].pop(-1)   
                    
            #if -1 in self.dialogue_participants[d_id]:
                #print(self.dialogue_participants[d_id])
                #print(self.dialogues[d_id])
                #print("----------------------")
                #print("Dialogue number: " + str(d_id))
                #print("Number of paragraphs: " + str(len(self.dialogues[d_id]))) 
                #print("---")
                #for char_id in self.dialogue_participants[d_id]:
                #    print(self.chars.get_name(char_id) + ": " + str(self.dialogue_participants[d_id][char_id]))
    
    
    def find_voc_mentions(self, aliases, p_id):
        mentions = self.mentions(p_id) # each mention = [char_id, isInsideQuote/vocative, [t_ids]]
        t_id = self.tks.paragraphs[p_id][0]
        
        while t_id in range(t_id, self.tks.paragraphs[p_id][-1] + 1):
            char_id = -1
            isInsideQuote = False
            isVocative = False
            t_ids = []
            
            if self.tks.char_id(t_id) == -1:
                for alias in aliases.keys():
                    if self.tks.word(t_id) == alias.split()[0]:
                        all_ids = list(range(t_id, t_id + len(alias.split()), 1))
                        if [self.tks.word(t_id) for t_id in all_ids] == alias.split():
                            #update tks info
                            for t_id in all_ids:
                                self.tks.add_char_id(t_id, aliases[alias])  
                            # update mentions info
                            t_ids = all_ids
                            if self.tks.quotation(t_ids[0]) == "true":
                                isInsideQuote = True
                            isVocative = self.isVocative(p_id, t_ids)
                            char_id = aliases[alias]      
                                
            # update t_id
            t_id += 1
            
            # update mentions only if there is a vocative pattern
            if t_ids != [] and isVocative:
                mention = [char_id, isInsideQuote, isVocative, t_ids]
                if mention not in mentions:
                    mentions.append(mention)
                    print(mention)
                    print(p_id)
                
        # add mentions to paragraphs_info
        self.paragraphs_info[p_id][1] = mentions

        return mentions
    
          
    #TODO: Check whether char is also mentioned inside quote  
    # Cross off participants from the list of dialogue participants that are most likely not the speaker of the utterance    
    def find_speaker_heuristics(self, d_id, p_id):
        #print(", ".join([self.chars.get_name(ptp) for ptp in self.dialogue_participants[d_id]]))
        #print(", ".join(list(set(self.chars.get_name(m[0]) for m in self.mentions(p_id)))))
        #all_mentions = []
        #for pid in self.dialogues[d_id]:
        #    all_mentions.extend(self.mentions(pid))
        #print(", ".join(list(set(self.chars.get_name(m[0]) for m in all_mentions))))
        #print(p_id)
        #print("---")
        
        # Remove the speakers of adjacent paragraphs from the candidates
        candidates = list(self.dialogue_participants[d_id].keys())
        if -1 in candidates:
            candidates.remove(-1)
        # remove previous speaker as one of the candidates    
        prev_pid = self.prev_pid(d_id, p_id)
        if prev_pid != -1 and self.speaker(prev_pid) != [] and self.speaker(prev_pid)[0] in candidates and prev_pid == p_id - 1:
            candidates.remove(self.speaker(prev_pid)[0])
        
        # remove next speaker as one of the candidates
        next_pid = self.next_pid(d_id, p_id)
        if next_pid != -1 and self.speaker(next_pid) != [] and self.speaker(next_pid)[0] in candidates and next_pid == p_id + 1:
            candidates.remove(self.speaker(next_pid)[0])
        
        if len(candidates) == 1:
            char_id = candidates[0]
            
            t_ids = []
            for pid in self.dialogues[d_id]:
                if self.speaker(pid) != []:
                    if self.speaker(pid)[0] == char_id:
                        t_ids = self.speaker(pid)[1:]
                        break
            self.add_speaker(d_id, p_id, char_id, t_ids)
            self.add_detected_pattern(p_id, "heuristics_1left")
        elif len(candidates) > 1:
            print(str(p_id) + ": " + " ".join([self.chars.get_name(candidate) for candidate in candidates]))
            
        return candidates
          
                
    def find_majority_speaker(self, d_id, p_id):
        
        # First try to find a majority speaker within the dialogue
        self.find_majority_speaker_in_(d_id, p_id, self.dialogues[d_id], "dlg_majority")
        
        # if dialogue only contains unknown speakers -> count speakers in the whole book and assign majority
        if self.speaker(p_id) == []:
            self.find_majority_speaker_in_(d_id, p_id, self.paragraphs_info, "all_majority")  

    # Given a list of paragraphs, decide the majority speaker in that list   
    def find_majority_speaker_in_(self, d_id, p_id, paragraphs, label):
        # create a dictionary of speakers with the number of occurrences in 
        count_speakers = {}
        for pid in paragraphs:
            speaker = self.speaker(pid)
            if speaker != []:
                if speaker[0] in count_speakers:
                    count_speakers[speaker[0]] += 1
                else:
                    count_speakers[speaker[0]] = 1
                    
        if count_speakers != {}:
            sorted_speakers = sorted(zip(count_speakers.values(), count_speakers.keys()), reverse=True)
            char_id = sorted_speakers[0][1]
            for pid in paragraphs:
                if self.speaker(pid) != []:
                    if self.speaker(pid)[0] == char_id:
                        t_ids = self.speaker(pid)[1:]
                        break
                        
            self.add_speaker(d_id, p_id, char_id, t_ids)
            self.add_detected_pattern(p_id, label)

 
    
    
########################################################################################################################      
                        
                                
                
    def speaker(self, p_id):
        return self.paragraphs_info[p_id][0]
        
    def add_speaker(self, d_id, p_id, char_id, t_ids):
        self.paragraphs_info[p_id][0] = [char_id]
        for t_id in t_ids:
            self.paragraphs_info[p_id][0].append(t_id)
            
        if char_id in self.dialogue_participants[d_id]:
            self.dialogue_participants[d_id][char_id].append(t_ids)
        else:
            self.dialogue_participants[d_id][char_id] = t_ids
    
    def mentions(self, p_id):
        return self.paragraphs_info[p_id][1]

    def current_turn(self, p_id):
        return self.paragraphs_info[p_id][2]
        
    def prev_pid(self, d_id, p_id):
        pid_index = self.dialogues[d_id].index(p_id)
        if pid_index == 0 or not isinstance(pid_index, int):
            return -1
        else:
            return self.dialogues[d_id][pid_index - 1]
            
    def next_pid(self, d_id, p_id):
        pid_index = self.dialogues[d_id].index(p_id)
        if pid_index > len(self.dialogues[d_id]) -2 or not isinstance(pid_index, int):
            return -1
        else:
            return self.dialogues[d_id][pid_index + 1]
        
    def quote(self, p_id):
        return self.paragraphs_info[p_id][3]
    
    def onlyQuote(self, p_id):
        return self.paragraphs_info[p_id][4]
        
    def narrative_word(self, p_id):
        return self.paragrahps_info[p_id][5]
        
    def adverbs(self, p_id):
        return self.paragraphs_info[p_id][6]
        
    def adjectives(self, p_id):
        return self.paragraphs_info[p_id][7]
        
    def add_detected_pattern(self, p_id, pattern):
        self.paragraphs_info[p_id][8] = pattern
       
    def detected_pattern(self, p_id):
        return self.paragraphs_info[p_id][8]
        
    def total_dialogues(self):
        return len(self.dialogues.keys())
        
    def total_paragraphs(self):
        return len(self.paragraphs_info.keys())
        
    def total_quotes(self):
        total = 0
        for d_id in self.dialogues:
            total += len(self.dialogues[d_id])
        
        return total
    
                
    
    
    #TODO: Change comma in full stop at end of sentence
    #TODO: Change comma in middle of quote if eos
    #TODO: Change first letter of first word of new sentence in middle and start of quote into capital  
    #TODO: Remove "--"
    def pretty_quote(self, quote, tks): 
        d_qt = ['\"', '“', '”']
        s_qt = ['\'', '‘', '’']
        punct = ['--',';',',']
        
        quote = quote[1:-1] # remove quotation marks
        #dummy = False
        
        #replace_punct = False # replace punct with full stop if not EOS marker
        #append_punct = False # Add full stop at end if missing
        #if quote != []:
        #    if tks.word(quote[-1]) != "." and tks.word(quote[-1]) != "?" and tks.word(quote[-1]) != "!" and tks.word(quote[-1]) != "...":
        #        if tks.word(quote[-1]) in punct:
        #            replace_punct = True
        #        else:
        #            append_punct = True
        #        dummy = True
                #print(tks.word(quote[-1]))
        
        
        snt = ""
        for t_id in quote:
            if tks.isDouble and tks.word(t_id) in d_qt and tks.word(quote[quote.index(t_id) + 1]) in d_qt:
                snt += " "
                del quote[quote.index(t_id) + 1]
            elif not tks.isDouble and tks.word(t_id) in s_qt and tks.word(quote[quote.index(t_id) + 1]) in s_qt:
                snt += " "
                del quote[quote.index(t_id) + 1]
            else:
                separation = tks.separation(t_id)
                if separation == "" or separation == "NN":
                    snt += tks.word(t_id)
                else:
                    snt += tks.word(t_id) + " "
        
        # Handle last t_id according to if needs to be replaced by full stop or not
        #if quote != []:
        #    if replace_punct == True:
        #        if snt[-1] == " ":
        #            snt = snt[:-1]
        #        if snt[-2:] == "--":
        #            snt = snt[:-2] + "."
        #        else:
        #            snt = snt[:-1] + "."
        #        snt += "."
        #    elif append_punct == True:
        #        snt[:-1] + "."
           
        
        
        
        #if dummy:
        #    print(snt)            
        
        return snt
 
    def statistics(self):
        statistics = {}
        for d_id in self.dialogues:
            for p_id in self.dialogues[d_id]:
                if self.detected_pattern(p_id) in statistics:
                    statistics[self.detected_pattern(p_id)] += 1
                else:
                    statistics[self.detected_pattern(p_id)] = 1 
        
        print("Statistics for the pattern detection algorithm:\n-----\n")
        for pattern in statistics:
            print(pattern + ": " + str(statistics[pattern]))
        print("-----")
        print("Total: " + str(self.total_quotes()))
            
 
    def write_dialogues(self, dl):
        with open(dl, 'w') as dlgs:
            for d_id in self.dialogues.keys():
                dlgs.write("Dialogue #" + str(d_id) + " - Dialogue Participants: " + ", ".join([self.chars.get_name(p) for p in self.dialogue_participants[d_id]]) + "\n")
                for p_id in self.dialogues[d_id]:
                    turn = self.current_turn(p_id)
                    speaker = self.speaker(p_id)
                    if speaker != []:
                        char_id = speaker[0]
                    else:
                        char_id = -1
                    utterance = self.quote(p_id)
                    dlgs.write("Rule: " + self.detected_pattern(p_id) + " --- " + "Turn " + str(turn) + ": " + str(p_id) + " -- " + self.chars.get_name(char_id) + " (" + str(char_id) + "): " + utterance + "\n")
                dlgs.write("\n")
                

    def print_dialogue(self, d_id):
        print("Dialogue #" + str(d_id) + " - Dialogue Participants: " + ", ".join([self.chars.get_name(p) for p in self.dialogue_participants[d_id]]))
        for p_id in self.dialogues[d_id]:
            turn = self.current_turn(p_id)
            speaker = self.speaker(p_id)
            if speaker != []:
                char_id = speaker[0]
            else:
                char_id = -1
            utterance = self.quote(p_id)
            mentions = ", ".join([self.chars.get_name(alias[0]) for alias in self.mentions(p_id)])
            print("Turn " + str(turn) + ": " + str(p_id) + " -- " + self.chars.get_name(char_id) + " (" + str(char_id) + "): " + utterance)
        print("\n\n")
    
        
if __name__ == "__main__":
    tks = TokenInfo(f)
    chars = CharacterInfo(tks)
    sua = SpeakerUtteranceAttribution(tks, chars)
    
    sua.tks.write_to_file("tks_info.txt")
    sua.write_dialogues("quotes.txt")
    sua.statistics()
    #for d_id in sua.dialogues:
    #    sua.print_dialogue(d_id)
        
