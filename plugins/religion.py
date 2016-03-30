from util import hook, http


@hook.command('god')
@hook.command
def bible(inp):
    ".bible <passage> -- gets <passage> from the Bible (ESV)"

    base_url = ('http://www.esvapi.org/v2/rest/passageQuery?key=IP&'
                'output-format=plain-text&include-heading-horizontal-lines&'
                'include-headings=false&include-passage-horizontal-lines=false&'
                'include-passage-references=false&include-short-copyright=false&'
                'include-footnotes=false&line-length=0&'
                'include-heading-horizontal-lines=false')

    text = http.get(base_url, passage=inp)

    text = ' '.join(text.split())

    if len(text) > 400:
        text = text[:text.rfind(' ', 0, 400)] + '...'

    return text


@hook.command('allah')
@hook.command
def koran(inp):  # Koran look-up plugin by Ghetto Wizard
    ".koran <chapter.verse> -- gets <chapter.verse> from the Koran"

    url = 'http://quod.lib.umich.edu/cgi/k/koran/koran-idx?type=simple'

    results = http.get_html(url, q1=inp).xpath('//li')

    if not results:
        return 'No results for ' + inp

    return results[0].text_content()

tao_text = ["""Tao called Tao is not Tao. Names can name no lasting name. 
Nameless: the origin of heaven and earth. Naming: the mother of ten thousand things. 
Empty of desire, perceive mystery. Filled with desire, perceive manifestations. 
These have the same source, but different names. 
Call them both deep - Deep and again deep: the gateway to all mystery.""",
"""Recognize beauty and ugliness is born. 
Recognize good and evil is born. 
Is and Isn't produce each other. Hard depends on easy, Long is tested by short, 
High is determined by low, Sound is harmonized by voice, After is followed by before. 
Therefore the sage is devoted to non action, Moves without teaching, 
Creates ten thousand things without instruction, Lives but does not own, Acts but does not presume, 
Accomplishes without taking credit. When no credit is taken, Accomplishment endures.""",
"""Don't glorify heroes, And people will not contend. 
Don't treasure rare objects, And no one will steal. 
Don't display what people desire, And their hearts will not be disturbed. 
Therefore, the Sage rules By emptying hearts and filling bellies, By weakening ambitions and strengthening bones; Leads people Away from knowing and wanting; 
Deters those who know too much From going too far: 
Practices non-action And the natural order is not disrupted.""",
"""Tao is empty- its use never exhausted. 
Bottomless - the origin of all things. 
It blunts sharp edges, Unties knots, Softens glare, Becomes one with the dusty world. 
Deeply subsistent - 
I don't know whose child it is. It is older than the Ancestor.""",
"""Heaven and Earth are not kind: The ten thousand things are straw dogs to them. 
The Sage is not kind: People are straw dogs to him. 
Yet Heaven and Earth And all the space between Are like a bellows: Empty but inexhaustible, Always producing more. 
Longwinded speech is exhausting. Better to stay centered.""",
"""The Valley Spirit never dies. It is called the Mysterious Female. 
The entrance top the Mysterious Female Is called the root of Heaven and Earth. 
Endless flow of inexhaustible energy.""",
"""Heaven is long, Earth enduring. 
Long and enduring Because they do not exist for themselves. 
Therefore the Sage Steps back, but is always in front, Stays outside, but is always within. 
No self-interest? 
Self is fulfilled?""",
"""Best to be like water, Which benefits the ten thousand things And does not contend. It pools where humans disdain to dwell, Close to the Tao. 
Live in a good place. Keep your mind deep. Treat others well. Stand by your word. 
Make fair rules. Do the right thing. Work when it's time. 
Only do not contend, And you will not go wrong.""",
"""Hold and fill it - No as good as stopping in time. 
Measure and pound it - It will not long survive. 
When gold and jade fill the hall, They cannot be guarded. 
Riches and pride Bequeath error. 
Withdrawing when work is done: Heaven's Tao.""",
"""Can you balance your life force And embrace the One Without separation? 
Can you control your breath Gently Like a baby? 
Can you clarify Your dark vision Without blemish? 
Can you love people And govern the country Without knowledge? 
Can you open and close The gate of heaven Without clinging to earth? 
Can you brighten The four directions Without action? 
Give birth and cultivate. Give birth and do not possess. Act without dependence. Excel but do not rule. This is called the dark Te.""",
"""Thirty spokes join one hub. The wheel's use comes from emptiness. 
Clay is fired to make a pot. The pot's use comes from emptiness. 
Windows and doors are cut to make a room. The room's use comes from emptiness. 
Therefore, Having leads to profit, Not having leads to use.""",
"""Five colors darken the eyes. Five tones darken the ears. Five tastes jade the palate. 
Hunting and racing madden the heart. Exotic goods ensnarl human lives. 
Therefore the Sage Takes care of the belly, not the eye, Chooses one, rejects the other.""",
"""Favour and disgrace are like fear. Honour and distress are like the self. 
What does this mean? Favour debases us. Afraid when we get it, Afraid when we lose it. 
The self embodies distress. No self, No distress. 
Respect the world as your self: The world can be your lodging. Love the world as your self: The world can be your trust.""",
"""Seeing but not seeing, we call it dim. Listening but not hearing, we call it faint. Groping but not touching, we call it subtle. 
These three cannot be fully grasped. Therefore they become one. 
Rising, it is not bright; setting it is not dark. It moves all things back to where there is nothing 
Meeting it there is no front, following it there is no back. 
Live in the ancient Tao, Master the existing present, Understand the source of all things. This is called the record of Tao.""",
"""The ancients who followed Tao: Dark, wondrous, profound, penetrating. Deep beyond knowing. 
Because they cannot be known, They can only be described. Cautious, like crossing a winter stream. Hesitant, like respecting one's neighbours. Polite, like a guest. 
Yielding, Like ice about to melt; Blank, like uncarved wood. Open, like a valley. Mixing freely, like muddy water. 
Calm the muddy water, It becomes clear. Move the inert, It comes to life.? 
Those who sustain Tao Do not wish to be full. Because they do not wish to be full They can fade away Without further effort.""",
"""Attain complete emptiness, Hold fast to stillness. 
The ten thousand things stir about; I only watch for their going back. Things grow and grow, But each goes back to its root. 
Going back to the root is stillness. This means returning to what is. Returning to what is Means going back to the ordinary. 
Understanding the ordinary: Enlightenment. Not understanding the ordinary: Blindness creates evil. Understanding the ordinary: Mind opens. Mind opening leads to compassion, Compassion to nobility, Nobility to heavenliness, Heavenliness to Tao. 
Tao endures. Your body dies. There is no danger.""",
"""Great rising and falling - People only know it exists. Next they see and praise. Soon they fear. Finally they despise. 
Without fundamental trust There is no trust at all. Be careful in valuing words. 
When the work is done, Everyone says We just acted naturally.""",
"""Great Tao rejected: Benevolence and righteousness appear. 
Learning and knowledge professed: Great Hypocrites spring up. 
Family relations forgotten: Filial piety and affection arise. 
The nation disordered: Patriots come forth.""",
"""Banish learning, discard knowledge: People will gain a hundredfold. 
Banish benevolence, discard righteousness: People will return to duty and compassion. 
Banish skill, discard profit: There will be no more thieves. 
These three statements are not enough. One more step is necessary. 
Look at plain silk; hold uncarved wood. The self dwindles; desires fade.""",
"""Banish learning, no more grief. Between Yes and No How much difference? Between good and evil How much difference?? 
What others fear I must fear - How pointless! 
People are wreathed in smiles As if at a carnival banquet. I alone am passive, giving no sign, Like an infant who has not yet smiles. Forlorn as if I had no home. 
Others have enough and more, I alone am left out. I have the mind of a fool, Confused, confused. 
Others are bright and intelligent, I alone and dull, dull, Drifting on the ocean, Blown about endlessly. 
Others have plans, I alone am wayward and stubborn, I alone am different from others, Like a baby in the womb.""",
"""Great Te appears Flowing from Tao. 
Tao in action - Only vague and intangible. Intangible and vague, But within it are images. Vague and intangible; Within are entities. Shadowy and obscure; Within there is life, Life so real, That within it there is trust. 
From the beginning its name is not lost But reappears through multiple origins. 
How do I know these origins? Like this.""",
"""Crippled become whole, Crooked becomes straight, Hollow becomes full, Worn becomes new, Little becomes more, Much becomes delusion. 
Therefore the Sages cling to the One And take care of this world; 
Do not display themselves And therefore shine. Do not assert themselves and therefore stand out. Do not praise themselves And therefore succeed. 
Do not contend And therefore no one under heaven Can contend with them. 
The old saying Crippled becomes whole Is not empty words. It becomes whole and returns.""",
"""Spare words; nature's way. Violent winds do not blow all morning. Sudden rain cannot pour all day. 
What causes these things? Heaven and Earth. If Heaven and Earth do not blow and pour for long, How much less should humans? 
Therefore in following Tao: Those on the way become the way, Those who gain become the gain, Those who lose become the loss. 
All within the Tao: The wayfarer, welcome upon the way, Those who gain, welcome within gain, Those who lose, welcome withon loss. 
Without trust in this, There is no trust at all.""",
"""Upon tiptoe: no way to stand. Clambering: no way to walk. 
Self-display: no way to shine. Self-assertion: no way to succeed. 
Self-praise: no way to flourish. Complacency: no way to endure. 
According to Tao, Excessive food, Extraneous activity Inspire disgust. Therefore the follower of Tao Moves on.""",
"""Something unformed and complete Before heaven and Earth were born, Solitary and silent, Stands alone and unchanging. Pervading all things without limit. It is like the mother of all things under heaven, 
But I don't know its name - Better call it Tao. Better call it great. 
Great means passing on. Passing on means going far. Going far means returning. 
Therefore Tao is great, And heaven, And earth, And humans. Four great things in the world. Aren't humans one of them? 
Humans follow earth Earth follows heaven Heaven follows Tao. Tao follows its own nature.""",
"""Gravity is the root of lightness, Stillness the master of passion. 
The Sage travels all day But does not leave the baggage-cart; When surrounded by magnificent scenery Remains calm and still. 
When a lord of ten thousand chariots Behaves lightly in this world, 
Lightness loses its root, Passion loses its master.""",
"""Good travelers leave no tracks. Good words leave no trace. Good counting needs no markers. 
Good doors have no bolts Yet cannot be forced. Good knots have no rope But cannot be untied. 
In this way the Sage Always helps people And rejects none, Always helps all beings, And rejects none. This is called practicing brightness. 
Therefore the good person is the bad person's teachers, And the bad person Is the good person's resource. 
Not to value the teacher, Not to love the resource, Causes great confusion even for the intelligent. This is called the vital secret.""",
"""Know the male, maintain the female, Become the channel of the world, And Te will endure. Return to infancy. 
Know the white, sustain the black, Become the pattern of the world, And Te will not falter. Return to the uncarved block. 
Know honour, sustain disgrace, Become the valley of the world, And Te will prevail. Return to simplicity. 
Simplicity divided becomes utensils That are used by the Sage as high official. But great governing does not carve up.""",
"""Trying to control the world? I see you won't succeed. 
The world is a spiritual vessel And cannot be controlled. Those who control, fail. Those who grasp, lose. 
Some go forth, some are led, Some weep, some blow flutes, Some become strong, some superfluous, Some oppress, some are destroyed. 
Therefore the Sage Casts off extremes, Casts off excess, Casts off Extravagance.""",
"""Use Tao to help rule people. This world has no need for weapons, Which soon turn on themselves. 
Where armies camp, nettles grow. After each war, years of famine. 
The most fruitful outcome Does not depend on force, 
But succeeds without arrogance Without hostility Without Pride Without resistance Without violence. 
If these things prosper and grow old, This is called not-Tao. Not-Tao soon ends.""",
"""Fine weapons are ill-omened tools. They are hated. Therefore the old Tao ignores them. 
At home, honour the left. In war, honor the right. 
Good omens honour the left. Bad omens honour the right. The lieutenant on the left, The general on the right As in funeral ceremonies. 
Weapons are ill-omened, Not proper instruments. When their use can't be avoided, Calm restraint is best. Don't think they are beautiful. Those who think they are beautiful Rejoice in killing people. 
Those who rejoice in killing people Cannot achieve their purpose in this world. 
When many people are killed We feel sorrow and grief. A great victory Is a funeral ceremony.""",
"""Tao endures without a name. Though simple and slight, No one under heaven can master it. 
If kings and lords could posses it, All beings would become their guests. 
Heaven and earth together Would drip sweet dew Equally on all people Without regulation. 
Begin to make order and names arise. Names lead to more names - And to knowing when to stop. 
Tao's presence in this world Is like valley streams Flowing into rivers and seas.""",
"""Knowing others is intelligent. Knowing yourself is enlightened. 
Conquering others takes force. Conquering yourself is true strength. 
Knowing what is enough is wealth. Forging ahead shows inner resolve. 
Hold your ground and you will last long. Die without perishing and your life will endure.""",
"""Great Tao overflows. To the left To the right. 
All beings owe their life to it And do not depart from it. It acts without a name. It clothes and nourishes all beings But does not become their master. 
Enduring without desires, It may be called slight. 
All beings return to it, But it does not become their master. It may be called immense. 
By not making itself great, It can do great things.""",
"""Hold the great elephant - The great image - And the world moves. Moves without danger in safety and peace. 
Music and sweets Make passing guests pause. 
But the Tao emerges Flavourless and bland. Look - you won't see it. Listen - You won't hear it. Use it - You will never use it up.""",
"""To collect, first scatter. To Weaken, first strengthen. To abolish, first establish. To conclude, first initiate. 
This is called subtle illumination. Soft and weak overcome stiff and strong. 
Fish cannot escape the deep pool. A country's sharpest weapons Cannot be displayed.""",
"""Tao endures without a name, Yet nothing is left undone. 
If kings and lords could possess it, All beings would transform themselves. Transformed, they desire to create; I quiet them through nameless simplicity. Then there is no desire. 
No desire is serenity, An the world settles of itself.""",
"""High Te? No Te! That's what Te is. Low Te doesn't lack Te; That's what Te is not. 
Those highest in Te take no action And don't need to act. Tose lowest in Te take action And do need to act. 
Those highest in benevolence take action But don't need to act. Those highest in righteousness take action And do need to act. Those highest in propriety take action And if people don't reciprocate Roll up their sleeves and throw them out. 
Therefore Lose Tao And Te follows. Lose Te and benevolence follows. Lose benevolence And righteousness follows. Lose righteousness and propriety follows. 
Propriety dilutes loyalty and sincerity: Confusion begins. Foreknowledge glorifies the Tao: Stupidity sets in. 
And so the ideal person dwells In substance, not dilution, In reality, not glory, Accepts one, rejects the other.""",
"""Of old, these attained the One: Heaven attaining the One Became clear. Earth attaining the One Became stable. Spirits attaining the One Became sacred. 
Valleys attaining the One Became bountiful. Myriad beings attaining the One Became fertile. Lords and kings attaining the One Purified the world. 
If Heaven were not clear It might split. If Earth were not stable It might erupt. If spirits were not sacred They might fade. 
If valleys were not bountiful They might wither. If myriad beings were not fertile, They might perish. If rulers and lords were not noble, They might stumble. 
Therefore, Noble has humble as its root, High has low as its foundation. 
Rulers and lords call themselves Poor and lonely orphans. Isn't this using humility as a root? 
They use many carriages But have no carriage;. 
They do not desire to glisten like jade But drop like a stone.""",
"""Reversal is Tao's movement. Yielding is Tao's practice. 
All things originate from being. Being originates from non-being.""",
"""The great scholar hearing the Tao Tries to practice it. The middling scholar hearing the Tao, Sometimes has it, sometimes not. 
The lesser scholar hearing the Tao Has a good laugh. Without that laughter It wouldn't be Tao. 
Therefore these sayings: The bright road seems dark, The road forward sees to retreat, The level road seems rough. 
Great Te seems hollow. Great purity seems sullied. Pervasive Te sees deficient. Established Te seems furtive. Simple truths seem to change. The great square has no corners. The great vessel is finished late. The great sound is scarcely voiced. The great image has no form. 
Tao hides, no name. Yet Tao alone gets things done.""",
"""Tao engenders One, One engenders Two, Two engenders Three, Three engenders the ten thousand things. 
The ten thousand things carry shade And embrace sunlight. Shade and sunlight, yin and yang, Breath blending into harmony. 
Humans hate To be alone, poor, and hungry. Yet kings and princes Use these words as titles. 
We gain by losing, Lose by gaining. 
What others teach, I also teach: A violent man does not die a natural death. This is the basis of my teaching.""",
"""The softest thing in the world rides roughshod over the strongest. No-thing enters no-space. This teaches me the benefits of no-action. 
Teaching without words Benefit without action - Few in this world can attain this.""",
"""Name or body: which is closer? Body or possessions: which means more? Gain or loss: Which one hurts? 
Extreme love exacts a great price. Many possessions entail a heavy loss. 
Know what is enough - Abuse nothing. Know when to stop - Harm nothing. This is how to last for a long time.""",
"""Great accomplishment seems unfinished But its use is continuous. Great fullness seems empty But in use is inexhaustible. 
Great straightness seems bent, Great skill seems clumsy, Great eloquence seems mute. 
Exertion overcomes cold. Calm overcomes heat. Pure calm is the norm under heaven.""",
"""With Tao under heaven Stray horses fertilize the fields. Without Tao under heaven Warhorses are bred at the frontier. 
There is no greater calamity Than not knowing what is enough. There is no greater fault Than desire for success. 
Therefore, Knowing that enough is enough Is always Enough.""",
"""Without going out the door, Know the world. Without peeping through the window, See heaven's Tao. The further you travel, The less you know. 
This is why the Sage Knows without budging, Identifies without looking, Does without trying.""",
"""Pursue knowledge, gain daily. Pursue Tao, lose daily. Lose and again lose, Arrive at non-doing. 
Non-doing - and nothing not done. 
Take the entire world as nothing. Make the least effort, And the world escapes you.""",
"""The Sage has no set heart. Ordinary people's hearts Become the Sage's heart. 
People who are good I treat well. People who are not good I also treat well: Te as goodness. 
Trustworthy people I trust. Untrustworthy people I also trust. Te as trust. 
Sages create harmony under heaven Blending their hearts with the world. Ordinary people fix their eyes and ears upon them, But Sages become the world's children.""",
"""Emerge into life, enter death, 
Life is only the thirteen body parts. Death is only the thirteen body parts. Human life, moving towards death, Is the same thirteen. Why is this? Because life gives life to substance. 
You have heard of people Good at holding on to life. Walking overland they don't avoid Rhinos and tigers. In battle they don't arm themselves. 
The rhino's horn find nothing to gore; The tiger's claws find nothing to flay, Weapons find nothing to pierce. Why is this? They have no mortal spot.""",
"""Tao bears them Te nurses them Events form them Energy completes them. Therefore the ten thousand beings Honour Tao and respect Te. Tao is honoured Te is respected Because they do not give orders But endure in their own nature. Therefore, Tao bears them and Te nurses them, Rears them, Raises them, Shelters them, Nurtures them, Supports them, Protects them. 
Bears them without owning them, Helps them without coddling them, Rears them without ruling them. This is called original Te.""",
"""The world has a source: the world's mother. Once you have the mother, You know the children. 
Once you know the children, Return to the mother. Your body dies. There is no danger. 
Block the passage, Bolt the gate: No strain Until your life ends. 
Open the passage, Take charge of things No relief Until your life ends. 
Seeing the small is called brightness Maintaining gentleness is called strength. 
Use this brightness to return to brightness. Don't cling to your body's woes. Then you can learn endurance.""",
"""Having some knowledge When walking on the Great Tao Only brings fear. 
The great Tao is very smooth, But people like rough trails. 
The government is divided, Fields are overgrown, Granaries are empty,. 
But the nobles clothes are gorgeous, Their belts show off swords, And they are glutted with food and drink. Personal wealth is excessive. This is called thieves' endowment, But it is not Tao.""",
"""Well planted, not uprooted. Well embraced, never lost. Descendants will continue The ancestral rituals. 
Maintain oneself: Te becomes real. Maintain the family: Te becomes abundant. Maintain the community: Te becomes extensive. Maintain the country: Te becomes public. Maintain the world: Te becomes omnipresent. 
Therefore, Through self contemplate self, Through family contemplate family, Through community contemplate community, Through country contemplate country, Through world contemplate world. 
How do I know the world? Like this!""",
"""Be filled with Te, Like a baby: Wasps, scorpions and vipers Do not sting it. Fierce tigers do not stalk it. Birds of prey do not attack it. Bones weak, muscles soft, But its grasp is tight. 
It does not yet know Union of male and female, But its sex is formed, Its vital essence complete. 
It can scream all day and not get hoarse, Its harmony is complete. Knowing harmony is called endurance. Knowing endurance is called illumination. 
Increasing life is called fortune. Mind controlling energy is called power. 
When beings prosper and grow old, Call them not-Tao. Not-Tao soon ends.""",
"""Those who know don't talk. Those who talk don't know. 
Block the passage Bolt the gate Blunt the sharp Untie the knot Blend with the light Become one with the dust - This is called original unity. 
It can't be embraced It can't be escaped, It can't be helped It can't be harmed, It can't be exalted It can't be despised, Therefore it is revered under Heaven.""",
"""Use the unexpected to govern the country, Use surprise to wage war, Use non-action to win the world. How do I know? Like this! 
The more prohibitions and rules, The poorer people become. The sharper people's weapons, The more they riot. 
The more skilled their techniques, The more grotesque their works. The more elaborate the laws, The more they commit crimes. 
Therefore the Sage says, I do nothing And people transform themselves. I enjoy serenity And people govern themselves. 
I cultivate emptiness And people become prosperous. I have no desires And people simplify themselves.""",
"""If government is muted and muffled People are cool and refreshed. If government investigates and intrudes, People are worn down and hopeless. 
Bad fortune rests upon good fortune. Good luck hides within bad luck. 
Who knows how it will end? If there is no principle Principle reverts to disorder, Good reverts to calamity, People's confusion hardens and lingers on. 
Therefore the Sage squares without cutting, Corners without dividing, Straightens without extending, Shines without dazzling.""",
"""Governing people and serving heaven Is like living off the land. 
Living sparingly and responding quickly Means accumulating Te. There is nothing that cannot be overcome. There is no limit. 
You can become the country And the country's mother, and nourish and extend it. 
This is called deep roots, firm base. This is the Tao of living long and seeing far.""",
"""Govern big countries Like you cook a little fish. 
When Tao harmonizes the world, Demons lose their power. 
Not that demons lose their power, but their power does not harm people. Not that their power does not harm people, but the Sage does not harm people. 
If neither does harm, Then Te flows and returns.""",
"""A great nation flows down To be the world's pool, The female under heaven In stillness The female constantly overcomes the male, In stillness Takes the low place. 
Therefore a great nation Lowers itself And wins over a small one. A small nation keeps itself low And wins over a great one. 
Sometimes becoming low wins, Sometimes staying low wins. 
A great nation desires nothing more Than to unite and protect people. A small nation desires nothing more Than to enter the service of people. 
When both get what they wish The great one should be low.""",
"""Tao is the mysterious center of all things, a treasure for those who are good, A refuge for those who are not. 
Beautiful words can be traded, Noble deeds can enhance reputations, But if people lack them, Why should they be rejected? 
When the Son of Heaven is enthroned And the Three Ministers installed, Presenting jade discs And four-horse chariots Cannot compare to sitting still And offering the Tao. 
The ancients honoured this Tao. Didn't they say: Through it seekers find, Through it the guilty escape? This is why Tao is honoured under Heaven.""",
"""Act without acting. Serve without serving. Taste without tasting. 
Big, little, Many, few, Repay hatred with Te. 
Map difficult with easy Approach great through narrow. 
The most difficult things in the world Must be accomplished through the easiest. The greatest things in the world Must be accomplished through the smallest. 
Therefore the Sage Never attempts great things and so accomplishes them. 
Quick promises Mean little trust. Everything easy Means great difficulty. 
Thus for the Sage everything is difficult, And so in the end Nothing is difficult.""",
"""At rest is easy to hold. Not yet impossible is easy to plan. Brittle is easy to break. Fine is easy to scatter. 
Create before it exists. Lead before it goes astray. 
A tree too big to embrace Is born from a slender shoot. A nine-story rises from a pile of earth. A thousand-mile journey Begins with a single step. 
Act and you ruin it. Grasp and you lose it. Therefore the Sage Does not act And so does not ruin Does not grasp And so does not lose. 
People commonly ruin their work When they are near success. Proceed at the end as at the beginning And your work won't be ruined. 
Therefore the Sage Desires no desires Prizes no prizes Studies no studies And returns To what others pass by. The Sage Helps all beings find their nature, But does not presume to act.""",
"""Taoist rulers of old Did not enlighten people But left them dull. 
People are difficult to govern Because they are very clever. Therefore, Ruling through cleverness leads to rebellion. Not leading through cleverness Brings good fortune. 
Know these two things And understanding the enduring pattern. Understand the enduring pattern: This is called original Te. 
Original Te goes deep and far. All things reverse Return And reach the great headwaters.""",
"""Rivers and seas Can rule the hundred valleys Because they are good at lying low They are lords of the valleys. 
Therefore those who would be above Must speak as if they are below Those who would lead Must speak as if they are behind. 
In this way the Sage dwells above And the people are not burdened. Dwells in front And they are not hindered. Therefore the whole world Is delighted and unwearied. 
Since the Sage does not contend No one can contend with the Sage.""",
"""Everyone under heaven calls my Tao great, and unlike anything else. It is great only because It is unlike anything else. If it were like anything else It would stretch and become thin. 
I have three treasures to maintain and conserve: the first is compassion. The second is frugality. The third is not presuming To be first under heaven. 
Compassion leads to courage. Frugality allows generosity. Not presuming to be first Creates a lasting instrument. 
Nowadays, People reject compassion But want to be brave, Reject frugality But want to be generous, Reject humility And want to come first. This is death. 
Compassion: Attack with it and win. Defend with it and stand firm. Heaven aids and protects Through compassion.""",
"""The accomplished person is not aggressive. The good soldier is not hot tempered. 
The best conqueror does not engage the enemy. The most effective leader takes the lowest place. 
This is called the Te of not contending. This is called the power of the leader. This is called matching Heaven's ancient ideal.""",
"""There is a saying in the army: I do not presume to be the master, But become the guest. I do not dare advance an inch, but retreat a foot. 
This is called moving without moving, rolling up sleeves without showing your arms, Repelling without opposing, Wielding without a weapon. 
There is no disaster greater than Contempt for the enemy. 
Contempt for the enemy - what a treasure is lost! Therefore, When the fighting gets hot, Those who grieve will conquer.""",
"""My words are very easy to understand, Very easy to practice. No one under heaven can understand them, No one can practice them. 
Words have ancestors, Deeds have masters. If people don't understand this, They don't understand me. Few understand me, And that is my value. 
Therefore the Sage wears rough clothing And carries Jade inside.""",
"""Know not-knowing: supreme. Not know knowing: faulty 
Only faulting faults is faultless. 
The Sage is faultless 
By faulting faults, 
And so is without fault.""",
"""When people are not in awe of power, Power becomes great. 
Do not intrude into their homes, Do not make their lives weary. If you do not weary them, They will not becoem weary of you. 
Therefore the Sage Has self-knowledge without self-display, Self-love without personal pride, Rejects one, accepts the other.""",
"""Courage to dare kills, Courage not to dare saves. One brings profit, one brings harm. 
Of these two, one is good, and one is harmful. Some are not favored by heaven. Who knows why? Even the wise consider it a difficult question. 
Heaven hates what it hates - Who knows why! Even the Sage finds it difficult. Heaven's Tao does not contend But prevails, Does not speak, But responds, Is not summoned, But arrives, Is utterly still, But plans all actions. 
Heaven's net is wide, wide, Loose - But nothing slips through.""",
"""If people do not fear death, How dare you threaten them with death? 
But if people with a normal fear of death Are about to do something vicious, And I could seize and execute them, Who would dare? 
There is always an official executioner. Trying to take the executioner's place, Is like trying to replace a master woodworker - Few would not slice their own hands.""",
"""People are hungry. When rulers tax grain People are hungry. 
People are rebellious. When rulers are active People are rebellious. 
People ignore death. When searching only for life's bounty People ignore death. Only those who do not strive after life Truly respect life.""",
"""Humans are born soft and weak. They die stiff and strong. 
The ten thousand plants and trees Are born soft tender, And die withered and sere. 
The stiff and strong Are Death's companions The soft and weak Are Life's companions. 
Therefore the strongest armies do not conquer, The greatest trees are cut down. 
The strong and great sink down. The soft and weak rise up.""",
"""Heaven's Tao Is a stretched bow, Pulling down on the top Pulling up on the bottom. 
If it's too much, cut. If it's not enough, Add on to it: Heaven's Tao. 
The Human Route Is not like this, Depriving the poor, Offering to the rich. Who has a surplus And still offers it to the world? Only those with Tao. 
Therefore the Sage Acts and expects nothing, Accomplishes and does not linger, Has no desire to seem worthy.""",
"""Nothing in the world is soft and weak as water. But when attacking the hard and strong Nothing can conquer so easily. 
Weak overcomes strong, soft overcomes hard. Everyone knows this, no one attains it. 
Therefore the Sage says: Accept a country's filth And become master of its sacred soil. Accepts country's ill fortune And become king under heaven. True words resemble their opposites.""",
"""Appears great hatred sand hatred will remain. How can this be good? 
Therefore the Sage Holds the tally But does not judge people. 
Those who have Te Control the tally. Those who lack Te Collect their due. 
Heaven has no favourites But endures in good people.""",
"""Small country, few people - Hundreds of devices, But none are used. People ponder on death And don't travel far. 
They have carriages and boats, But no one goes on board; Weapons and armour, But no one brandishes them. 
They use knotted cords for counting. Sweet is their food, Beautiful their clothes, Peaceful their homes, Delightful their customs. 
Neighboring countries are so close You can hear their chickens and dogs. But people grow old and die Without needing to come and go.""",
"""Sincere words and not pretty. Pretty words are not sincere. 
Good people do not quarrel. Quarrelsome people are not good. 
The wise are not learned. The learned are not wise. 
The Sage is not acquisitive - Has enough By doing for others, Has even more By giving to others. 
Heaven's Tao Benefits and does not harm. The Sage's Tao Acts and does not contend."""]

@hook.command('laozi')
@hook.command
def tao(inp):
    ".tao <chapter:line> -- gets line <line> from chapter <chapter> of the Tao Te Ching (Addiss)"

    if ':' not in inp:
        return tao.__doc__

    chapter, line = inp.split(':', 1)

    try:
        chapter = int(chapter)
        line = int(line)
    except ValueError:
        return tao.__doc__

    if chapter > len(tao_text):
        return "Chapter {} not found. Valid chapters: 1-{}".format(chapter, len(tao_text))

    target_chapter = tao_text[chapter - 1].split("\n")

    if line > len(target_chapter):
        return "Line not found. Valid lines: 1-%(lines)" % {"lines": len(target_chapter)}

    return target_chapter[line - 1]
