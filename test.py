from main import security,get_songs,better_recs,make_playlist

# These are three instances of how to successfully get a playlist of songs based on your current playlists!
# IMPORTANT: The playlist has to include some songs from the data.csv or it will not work.

ls = get_songs("4n9ydAkke9eUrWUDSzf1Nm")
recs = better_recs([0,100],"data.csv",ls)
make_playlist(recs,"Soft n soft")

ls2 = get_songs("7k1SjnkYpYBKay7xxetNus")
recs = better_recs([0,100],"data.csv",ls2)
make_playlist(recs,"Based on spring '21 playlist")

ls2 = get_songs("4umSURP4oofkfjrfCiOpLw")
recs = better_recs([0,100],"data.csv",ls2)
make_playlist(recs,"Based on Kpop")