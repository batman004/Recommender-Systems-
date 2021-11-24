
using Base: @_propagate_inbounds_meta
using CSV
using DataFrames
using Statistics
using DataFramesMeta
using BenchmarkTools
using LoopVectorization


function recommender(id)

    ratings=DataFrame(CSV.File("ratings.csv"))
    ratings = select!(ratings,Not(:"timestamp"))
    movies = DataFrame(CSV.File("movies.csv"))
    movies = select!(movies,Not(:"genres"))
    ratings = innerjoin(ratings, movies, on = :movieId)
    movieRatings=unstack(ratings,:"userId",:"title",:"rating",allowduplicates=true)

    movieRatings_matrix=movieRatings

    @simd for col in eachcol(movieRatings_matrix)
        replace!(col,missing => 0)
    end

    # movieRatings_matrix = select!(movieRatings_matrix, Not(:"userId"))


    movieRatings_matrix1=movieRatings_matrix

    movieRatings_matrix1 = select(movieRatings_matrix1, Not(:"userId"))

    movieRatings_matrix1 = Matrix(movieRatings_matrix1)

    corrMatrix = cor(movieRatings_matrix1)

    availability_matrix = movieRatings_matrix1

    # availability_matrix=map(x -> isnan(x) ? zero(x) : x/x, availability_matrix)

    availability_matrix=map(x -> iszero(x) ? 0.0 : x/x, availability_matrix)

    customer_Rating_count = availability_matrix' * availability_matrix 

    threshold_matrix=map(x -> x>100.0 ? 1.0 : NaN, customer_Rating_count)

    final_corr_matrix = corrMatrix .* threshold_matrix

    #Get movie ratings for an individual user :

    myRatings=@subset(movieRatings, in([id]).(:userId))

    myRatings = select(myRatings, Not(:"userId"))
    myRatings =stack(myRatings,:)
    myRatings=dropmissing(myRatings)
    rename!(myRatings, [:variable, :value] .=>  [:title, :Rating])
    myRatings=filter(:Rating => Rating -> ! iszero(Rating), myRatings)
    myRatings = innerjoin(myRatings, movies, on = :title)
    # myRatings=sort(myRatings,:Rating,rev=true)


    # id_title_dict=Dict(Pair.(movies.movieId, movies.title))

    my_movie_ratings = Array(myRatings.movieId)
    len=length(my_movie_ratings)
    my_movie_ratings
    simCandidates = []
    # ssims=[]

    @simd for i=1:len
    #     println("for movie :",my_movie_ratings[i]," ",id_title_dict[my_movie_ratings[i]])
        sims=filter(!isnan, final_corr_matrix[my_movie_ratings[i],:])
        
        # global ssims=push!(ssims,[sims])
        #Scale the similar movies according to rating of user, 
        #eg: if user has given 5 to Titanic, a movie similar to titanic would be scaled by 5
        
        Ssims=map((x) -> x*my_movie_ratings[i],sims)
        
        # print(sims)
        simCandidates=push!(simCandidates,Ssims)
        println(simCandidates[i])
    end

end

userid=20
print(@benchmark recommender(userid))
