import os
import re
f = "book-nlp/data/tokens/dickens.oliver.tokens"
#f = "book-nlp/data/tokens/austen.sense.tokens"
#f = "book-nlp/data/tokens/austen.pride.tokens"

def extract_quotes():
    with open(f, 'r') as tks:
        said = {}
        s_id = 0
        p_id = 0
        index = str(p_id) + " " + str(s_id)
        s = []
        
        for line in tks:
            l = line.split('\t')
            new_p_id = l[0]
            new_s_id = l[1]
            new_index = str(new_p_id) + " " + str(new_s_id)
            
            if new_index != index:
                if s != []:
                    said[index] = s
                    s = []
                    
                index = new_index
                
                
            # Condition of which sentences to use
            if l[13] == "true":
                s.append(l[9])
    
    #for snt in said.keys():
    #    print(" ".join(said[snt]))

def get_paragraphs(f):
    with open(f, 'r') as tks:
        paragraphs = {}
        
        s = []
        prev_id = 0
        
        tks_info = {} # list of info per feature
        next(tks)
        for line in tks:
            l = line.split('\t')
            p_id = l[0]
            tk_id = l[2]
            tk = l[7]
            #del l[2:5]
            tks_info[tk_id] = l
            
            if not p_id in paragraphs.keys():
                paragraphs[p_id] = []
            
            paragraphs[p_id].append((tk, tk_id))
    
    return(tks_info, paragraphs)
    
    
def add_quotations(tks_info, paragraphs):
    all_qt_marks = ['\"', '\'', '“', '”', '‘', '’']
    d_qt_marks = ['\"', '“', '”']
    s_qt_marks = ['\'', '‘', '’']
    punct = [',','.','!',':']

    # decide way of quoting by counting total quotation marks of each type
    c_d = 0
    c_s = 0
    for p in paragraphs:
        for w in paragraphs[p]:
            if w[0] in d_qt_marks:
                c_d += 1
            elif w[0] in s_qt_marks:
                c_s += 1
                
    if c_d > c_s:
        qt_marks = d_qt_marks
    else:
        qt_marks = s_qt_marks
        

    for p in paragraphs.keys():
        c_qt = 0
    
        for w in paragraphs[p]:
        
            if w[0] in qt_marks:
                # Check if quotation mark is possesive
                if (tks_info[w[1]][10] != "POS"):
                    c_qt += 1
                    tks_info[w[1]][13] = "quotation"
                else:
                    tks_info[w[1]][13] = "false"
            else: 
                tks_info[w[1]][13] = "false"
        
        words = [w for w in paragraphs[p]]
        
        if c_qt == 0:
            pass
            
        # If there is only one quotation mark, it cannot be part of direct speech, so change it back to false        
        elif c_qt == 1:
            for w in words:
                if w[0] in qt_marks:
                    tks_info[w[1]][13] = "false"    
        
        
        elif c_qt == 2:
                
            # Find first and last instance of quotation mark
            first_qt = next((w for w in words if tks_info[w[1]][13] == "quotation"), ("false",0))
            last_qt = next((w for w in list(reversed(words)) if tks_info[w[1]][13] == "quotation"), ("false",0))
            
            
            first_i = int(first_qt[1])
            last_i = int(last_qt[1])
            
            
            if c_d <= c_s:
                
                if tks_info[str(last_i - 1)][10] in all_qt_marks:
                    prev_tk = str(last_i - 2)
                else: 
                    prev_tk = str(last_i - 1)
               
               
                if tks_info[prev_tk][10] in punct: 
                        
                    for w in words:
                                
                        if int(w[1]) < first_i or int(w[1]) > last_i:
                            tks_info[w[1]][13] = "false"
                        else:
                            tks_info[w[1]][13] = "true"  
             
                else:
                    for w in words:
                        tks_info[w[1]][13] = "false"  
                                                 
            else:
                for w in words:
                            
                    if int(w[1]) < first_i or int(w[1]) > last_i:
                        tks_info[w[1]][13] = "false"
                    else:
                        tks_info[w[1]][13] = "true"  
            
            
        elif c_qt == 3:
            # Find first and last instance of quotation mark
            first_qt = next((w for w in words if tks_info[w[1]][13] == "quotation"), ("false",0))
            offset = int(first_qt[1]) - int(words[0][1])
            middle_qt = next((w for w in words[offset:] if tks_info[w[1]][13] == "quotation"), ("false",0))
            last_qt = next((w for w in list(reversed(words)) if tks_info[w[1]][13] == "quotation"), ("false",0))
            
            
            first_i = int(first_qt[1])
            middle_i = int(middle_qt[1])
            last_i = int(last_qt[1])
            
            #print([w[0] for w in words]) 
            
            if tks_info[str(middle_i - 1)][10] in all_qt_marks:
                m_prev_tk = str(middle_i - 2)
            else: 
                m_prev_tk = str(middle_i - 1)
                
                
            if tks_info[str(last_i - 1)][10] in all_qt_marks:
                l_prev_tk = str(last_i - 2)
            else: 
                l_prev_tk = str(last_i - 1)
            
            
            if first_i == int(words[0][1]) and tks_info[l_prev_tk][10] in punct:
                for w in words:
                            
                    if int(w[1]) < first_i or int(w[1]) > last_i:
                        tks_info[w[1]][13] = "false"
                    else:
                        tks_info[w[1]][13] = "true" 
                #print([w[0] for w in words])            
            
            
            elif first_i == int(words[0][1]) and tks_info[m_prev_tk][10] in punct:
                for w in words:
                            
                    if int(w[1]) < first_i or int(w[1]) > middle_i:
                        tks_info[w[1]][13] = "false"
                    else:
                        tks_info[w[1]][13] = "true" 
                #print([w[0] for w in words]) 
            
            else:
                for w in words:
                    tks_info[w[1]][13] = "false"   
           
            
        elif c_qt % 2 == 0:
            quotes = [w for w in words if tks_info[w[1]][13] == "quotation"]
            total = len(quotes)
            
            #only if single quotes, double quotes almost always mean direct speech
            if c_d <= c_s:
                    
                #print([w[0] for w in words])
                #check previous symbol
                prec_by_punct = True
                for q in quotes:
                    q_i = int(q[1])
                
                    if tks_info[str(q_i - 1)][10] in all_qt_marks:
                        prev_tk = str(q_i - 2)
                    else: 
                        prev_tk = str(q_i - 1)
                    
                    if q_i == int(words[0][1]) or tks_info[prev_tk][10] in punct:
                        pass
                    else:
                        quotes.remove(q)
                        #print([w[0] for w in words])
           
            if len(quotes) % 2 == 0:
                mark_as = False
                
                for w in words:
                    last_qt = False
                    if w in quotes and mark_as == False:
                        mark_as = True
                    elif w in quotes and mark_as == True:
                        mark_as = False
                        last_qt = True
                        
                    if mark_as == True or last_qt:
                        tks_info[w[1]][13] = "true"
                    else:
                        tks_info[w[1]][13] = "false"
            else:
                #print([w[0] for w in words])
                for w in words:
                    tks_info[w[1]][13] = "false"
                
            
            
            """
            # case of 2 or 3 instances: All quotation marks within quotes are most probably not relevant 
            # ignore the 3rd instance as it is not relevant and prob the last instance is the correct one 
            # Also we only deal with quotes when the last qt mark is preceded by punctuation symbol  
            if tks_info[str(last_i - 1)][10] not in qt_marks:
                prev_tk = str(last_i - 1)
            else: 
                prev_tk = str(last_i - 2)
            
            
            if c_qt == 2:
            
                # Also we only deal with quotes when the last qt mark is preceded by punctuation symbol 
                if tks_info[prev_tk][10] in punct: 
                    
                    for w in words:
                        
                        if int(w[1]) < first_i or int(w[1]) > last_i:
                            tks_info[w[1]][13] = "false"
                        else:
                            tks_info[w[1]][13] = "true"
                else:
                    pass               
                    
            elif (c_qt == 3):
                print(words)
                #if tks_info[prev_tk][10] in punct: 
            """     
             
        """        
        if qt_s > 6:
            print("Single:" + str(qt_s))
            print("Double:" + str(qt_d))
            print([w[0] for w in paragraphs[p]])
        elif qt_d > 6:
            print("Single:" + str(qt_s))
            print("Double:" + str(qt_d)) 
            print([w[0] for w in paragraphs[p]])   
        #if qt_s + qt_d > 6:
        #    print("QT:" + str(qt_s + qt_d)) 
        #    print([w[0] for w in paragraphs[p]])
        """
    return tks_info


def get_quotes(tks_info, paragraphs):
    quotes = []
    for p in paragraphs:
        quote = []
        for t in paragraphs[p]:
            if tks_info[t[1]][13] == "true":
                quote.append(t)
        if quote != []:
            quotes.append(quote)
  
    return quotes

def pretty_quotes(tks_info, quotes):
    d_qt = ['\"', '“', '”']
    s_qt = ['\'', '‘', '’']
    punct = ['.','!','?']
    # first word in first quote is always qt mark 
    if quotes[0][0][0] in ['\"', '“', '”']:
        isDouble = True
    else:
        isDouble = False
    
    qt_list = []    
          
    for quote in quotes:
        snt = ""
        for w in quote:
            if isDouble and w[0] in d_qt:
                pass
            elif not isDouble and w[0] in s_qt:
                pass
            elif w[0] == ',' and tks_info[str(w[1])][8] in d_qt and isDouble:
                snt += " "
            elif w[0] == ',' and tks_info[str(w[1])][8] in s_qt and not isDouble:
                snt += " "
            else:
                separation = tks_info[w[1]][5]
                if separation == "" or separation == "NN":
                    snt += w[0]
                else:
                    snt += w[0] + " "
        #print(snt)    
        qt_list.append(snt)
    return qt_list
    
    
def get_alias(tks_info, word_id):
    alias = []
    word = tks_info[word_id]
    if word[14] != "-1\n":
            if word[10] !=  "PRP$" or word[10] != "PRP": # ignore pronouns
                
                char_i = int(re.sub("\n", "", word[14]))
                new_char_i = char_i
                j = 1
                while char_i == new_char_i:
                    alias.append((tks_info[str(int(word_id)+j-1)][7], str(int(word_id)+j-1), int(re.sub("\n", "", word[14]))))
                    try: # avoid j becoming out of bounce
                        new_char_i = int(re.sub("\n", "", tks_info[str(int(word_id)+j)][14]))
                    except KeyError:
                        new_char_i = -1
                    j += 1
    
    return alias 
    
# Get list of characters with aliases, ignore PRP, only look at NNP
def aliases_list(tks_info, paragraphs):
    aliases = {} # i is key, list of aliases as values
    pronouns = {} # list of pronouns used, for that person (for gender identification)
    for i in range(0, len(tks_info)):
        word = tks_info[str(i)]
        
        if word[14] != "-1\n":
            if word[10] ==  "PRP$" or word[10] == "PRP": # ignore pronouns
                char_i = int(re.sub("\n", "", word[14]))
                prp = word[7].lower()
                if char_i in pronouns.keys():
                    if not prp in pronouns[char_i].keys():
                        pronouns[char_i][prp] = 1
                    else:
                        pronouns[char_i][prp] += 1
                else:
                    pronouns[char_i] = {prp: 1}
                  
            else:
                char_i = int(re.sub("\n", "", word[14]))
                new_char_i = char_i
                j = 1
                alias = ""
                
                while char_i == new_char_i:
                    alias += " " + tks_info[str(i+j-1)][7]
                    try: # avoid j becoming out of bounce
                        new_char_i = int(re.sub("\n", "", tks_info[str(i+j)][14]))
                    except KeyError:
                        new_char_i = -1
                    j += 1
                    
                alias = re.sub("^\s", "", alias) # remove initial space
                if char_i in aliases.keys():
                    if not alias in aliases[char_i]:
                        aliases[char_i].append(alias)
                else:
                    aliases[char_i] = [alias]
                    
    return aliases, pronouns
    
    
def gender_classifier(tks_info, aliases, pronouns):
    gender_list = {}
    
    male_pronouns = set(["he","his","him","himself"])
    female_pronouns = set(["she","her","herself"])
    male_indications = set(["mr","sir","mr.", "mister"])
    female_indications = set(["mrs","madame","miss","lady", "mrs.", "ms.","ms","missis", "missus"])
    
    for i in aliases:
        gender = "u" # u for unknown/undecided
        m_ind = False
        f_ind = False
        m = 0
        f = 0
    
        for a in aliases[i]:
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
            if i in pronouns.keys():
                for prp in pronouns[i].keys():
                    if prp in male_pronouns:
                        m += pronouns[i][prp]
                    elif prp in female_pronouns:
                        f += pronouns[i][prp]
            if m > f:
                gender = "m"
            elif f > m:
                gender = "f"        
    
        gender_list[i] = gender
        
        #print(aliases[i][0] + ": " + gender + " - " + str(m) + ", " + str(f))
        
    return gender_list


def speaker_utterance_attribution(tks_info, paragraphs, aliases):
    narrative_words = set(["hissed","declared","repeated","said","asked","replied","answered","cried","responded","added","screamed","wondered",
"reflected","pondered","ejaculated","rejoined","inquired", "says", "announced", "offered", "began","continued",
"mumbled","whispered","roared", "retorted", "sneered", "resumed", "added", "observed", "returned"])

    c_i = 1 # chapter number
    d_i = 0 # number of paragraphs between quoted speech
    dialogue_participants = [] # participants in current dialogue
    dialogues = [] # list of utterances for each dialogue
    
    narrative_i = 3 # check on i-3,...,i+3 if contains a name
    
    for p in paragraphs:
        quote = [] # current quote
        alias = [] # person uttering quote
        for word in paragraphs[p]:
            if tks_info[word[1]][13] == "true":
                quote.append(word)
            elif word[0].lower() in narrative_words:
                word_index = int(word[1])
                for i in range(word_index - narrative_i, word_index + narrative_i + 1): 
                    if tks_info[str(i)][13] == "false":
                        alias = get_alias(tks_info, str(i))
                    if alias != []:
                        break
        
        if alias != [] and quote != []:
            #print(" ".join(str(w[0]) for w in alias) + "-" + str(alias[0][2]) + ": " + " ".join([w[0] for w in quote]))
            continue
        elif quote != []:
            print(" ".join([w[0] for w in quote]))
            
                    
                # check next n and previous n words to list if 
            
    
        # if paragraph contains quotation
            # if paragraph has narrative word in it
                # get speaker using aliases
            # elif paragraph contains non-quoted speech
                # if contains name between quoted speech -> assign name to utterance
                # elif contains name outside quoted speech
                    # choose name closest to quoted speech
            # elif previous paragraph contained quotation
                # check speaker of that paragraph and speaker of i-2 paragraphs (recursive process)
                # if speaker of 
        

    return True

if __name__ == "__main__":

    tks_info, paragraphs = get_paragraphs(f)
    
    ps = add_quotations(tks_info, paragraphs)
     
    aliases, pronouns = aliases_list(tks_info, paragraphs) 
    genders = gender_classifier(tks_info, aliases, pronouns)
    #print(genders)
    #print(aliases)
    
    speaker_utterance_attribution(tks_info, paragraphs, aliases)
    
    #quotes = get_quotes(ps, paragraphs)
    
    #quotes = pretty_quotes(tks_info, quotes)     
    
    #for quote in quotes:
    #    print(quote)
    
    #for quote in quotes:
    #    print(" ".join(quote)) 
            
    """    
    if s_id == prev_id:
        s.append(tk)
    else:
        print(" ".join(s) + "\n")
        prev_id = s_id
        s = []
    """
            #else:
            #    quotes
            
            
                
            
