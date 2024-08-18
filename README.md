Documentation for the terms that are going to be used within the data along with trying to remember key decisions that I make
Label - This is the response variable. Either Favourite or Underdog will win\n",
    "* REACH - Fighter's reach. (Probabaly the least important feature)\n",
    "* SLPM - Significant Strikes Landed per Minute\n",
    "* STRA. - Significant Striking Accuracy\n",
    "* SAPM - Significant Strikes Absorbed per Minute\n",
    "* STRD - Significant Strike Defence (the % of opponents strikes that did not land)\n",
    "* TD - Average Takedowns Landed per 15 minutes\n",
    "* TDA - Takedown Accuracy\n",
    "* TDD - Takedown Defense (the % of opponents TD attempts that did not land)\n",
    "* SUBA - Average Submissions Attempted per 15 minutes\n",
    "* Odds - Difference between fighters A odds and fighter B's odds for that specific matchup "

    
The method I used to calculate the odds delta for each fight is as follows:

Identification of Odds: In the underdogvsfavoriteodds_data dataset, each fight had two odds listed: one for "Fighter A" and one for "Fighter B." These odds represent the likelihood of each fighter winning the match, as determined by the bookmakers.

Determination of Favorite and Underdog: The dataset identified which fighter was the favorite and which was the underdog. Typically, the fighter with the lower odds is the favorite (since lower odds indicate a higher probability of winning).

Calculation of Odds Delta: The delta (difference) between the odds of the favorite and the underdog was calculated as follows:

Odds Delta
=
Odds A
−
Odds B
Odds Delta=Odds A−Odds B
Here:

"Odds A" is the odds associated with "Fighter A."
"Odds B" is the odds associated with "Fighter B."
Merge with End Results: After calculating the Odds Delta, this value was merged with the End_Results dataset based on matching the event title, underdog, and favorite fighter names.

This Odds Delta provides an insight into how significant the difference in expected performance was between the favorite and the underdog, as perceived by the bookmakers. A positive delta suggests that the odds for the favorite were higher than those for the underdog, and a negative delta indicates the opposite.
