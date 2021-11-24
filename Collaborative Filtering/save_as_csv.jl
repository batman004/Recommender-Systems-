using CSV
using DataFrames
using DataFramesMeta

ratings_dat = DataFrame(CSV.File("ratings.dat"; header=false, delim = "::" ))
rename!(ratings_dat, [:userId, :movieId, :rating, :timestamp ])
ratings_dat = select!(ratings_dat,Not(:"timestamp"))
movies_dat = DataFrame(CSV.File("movies.dat"; header=false, delim = "::" ))
rename!(movies_dat, [:movieId, :title, :genres ])
movies_dat = select!(movies_dat,Not(:"genres"))
ratings_dat = innerjoin(ratings_dat, movies_dat, on = :movieId)
movieRatings_dat=unstack(ratings_dat,:"userId",:"title",:"rating",allowduplicates=true)

CSV.write("/Users/yuvraj/Desktop/WORK/JULIA/new/ratings_unstacked_10M.csv", movieRatings_dat)