

let ic = open_in "entrees.txt";;
let instant = float_of_string (input_line ic) ;;
let player = int_of_string (input_line ic) ;;
let dimensions = List.filter (fun x->x<>"") (String.split_on_char ' ' (input_line ic)) ;;
let lignes = int_of_string (List.hd dimensions) ;;
let colonnes = int_of_string (List.hd (List.tl dimensions)) ;;
let grille = Array.make_matrix lignes colonnes (-1) ;;
for i = 0 to lignes-1 do
    let l = List.filter (fun x->x<>"") (String.split_on_char ' ' (input_line ic)) in
    for j = 0 to colonnes-1 do
        grille.(i).(j) <- int_of_string (List.nth l j);
    done;
done;;


let nb_bombes = int_of_string (input_line ic) ;;
let bombes = Array.make_matrix nb_bombes 4 (-1.) ;;
for i = 0 to nb_bombes-1 do 
    let l = List.filter (fun x->x<>"") (String.split_on_char ' ' (input_line ic)) in
    for j = 0 to 3 do 
        bombes.(i).(j) <- float_of_string (List.nth l j);
    done;
done;;
let grille_bombes = Array.make_matrix lignes colonnes [||] ;;
for k = 0 to nb_bombes-1 do
    grille_bombes.( int_of_float bombes.(k).(0)).(int_of_float bombes.(k).(1))<-bombes.(k)
done;;



let swap a i j =
    let temp=a.(i) in
    a.(i)<-a.(j);
    a.(j)<-temp;;


let nb_joueurs = int_of_string (input_line ic) ;;
let joueurs = Array.make_matrix 4 8 (-1) ;;
for i = 0 to (nb_joueurs-1) do 
    let l =List.filter (fun x->x<>"") (String.split_on_char ' ' (input_line ic)) in
    for j = 0 to 7 do 
        joueurs.(i).(j) <- int_of_string (List.nth l j);
    done;
done;;


let i = ref 0 in
while !i <= 3 do
    if joueurs.(!i).(0)<>(-1) then
        if !i <> joueurs.(!i).(2) then
        swap joueurs (!i) (joueurs.(!i).(2))
        else incr i
    else incr i
done;;



let nb_powerups = int_of_string (input_line ic) ;;
let powerups = Array.make_matrix nb_powerups 3 (-1) ;;
for i = 0 to nb_powerups-1 do 
    let l =List.filter (fun x->x<>"") (String.split_on_char ' ' (input_line ic)) in
    for j = 0 to 2 do 
        powerups.(i).(j) <- int_of_string (List.nth l j);
    done;
done;;


let i, j =
    if joueurs.(player).(0) <> -1 && joueurs.(player).(1) <> -1 then
      (joueurs.(player).(0), joueurs.(player).(1))
    else
      (0, 0);;


let check_bombes_d i j d s =
    let dangers = ref [] in
    let vi, vj = if d = 0 then (s, 0) else (0, s) in
    let ip, jp = ref i, ref j in
    while ((!ip) >= 0) && ((!ip) < lignes) && ((!jp) >= 0) && ((!jp) < colonnes) && (grille.(!ip).(!jp) <> 1) && (grille.(!ip).(!jp) <> 2) do
        if grille_bombes.(!ip).(!jp) <> [||] &&
           grille_bombes.(!ip).(!jp).(2) >= float_of_int (max (abs (!ip - i)) (abs (!jp - j))) then
            dangers := (!ip, !jp) :: (!dangers);
        ip := !ip + vi;
        jp := !jp + vj;
    done;
    !dangers

let comparer a b =
    int_of_float (a -. b);;

let danger_c i j = (check_bombes_d i j 0 1)@((check_bombes_d i j 0 (-1))@((check_bombes_d i j 1 1)@(check_bombes_d i j 1 (-1))));;
let danger i j = 
    if i < 0 || i >= lignes || j < 0 || j >= colonnes ||
        i < 0 || i >= lignes || j < 0 || j >= colonnes then
         failwith "Invalid bomb coordinates in danger function";
    List.sort (fun (i1,j1) (i2,j2) -> comparer (grille_bombes.(i1).(j1).(3)) (grille_bombes.(i2).(j2).(3))) (danger_c i j);;

let voisins i j = [|(i-1,j);(i,j+1);(i+1,j);(i,j-1)|];;

exception Found of int*int;;

let largeur_voisins i j =
    let aux i j =
        let q = Queue.create () in
        let visited = Array.make_matrix lignes colonnes false in
        Queue.push (i,j) q;
        while not (Queue.is_empty q) do
            let (k,l) = Queue.pop q in
            visited.(k).(l) <- true;
            if (grille.(k).(l) <> (3+player))&&(grille.(k).(l)<>1) then
                raise (Found (k,l))
            else begin
                let v = voisins k l in
                for n = 0 to 3 do
                    if (((fst v.(n))>=0 && (fst v.(n))<lignes && (snd v.(n))>=0 && (snd v.(n))<colonnes))&&(not visited.(fst v.(n)).(snd v.(n))) then
                        Queue.push v.(n) q;
                done
            end
        done;
        (i,j)
    in try aux i j with
|Found (k,l) -> (k,l);; 



let valide i j = (i<lignes)&&(i>0)&&(j<colonnes)&&(j>0);;
let possible i j d = 
    if d = 4 then true
    else 
        let v = (voisins i j).(d) in
        (valide (fst v) (snd v))&&(grille.(fst v).(snd v)<>1)&&(grille.(fst v).(snd v)<>2)&&(grille_bombes.(fst v).(snd v)=[||])
    ;;
let possible2 i j d =
    if d = 4 then true
    else
        let v = (voisins i j).(d) in
        (valide (fst v) (snd v))&&(grille.(fst v).(snd v)<>1)&&(grille.(fst v).(snd v)<>2)&&(grille_bombes.(fst v).(snd v)=[||])&&(danger (fst v) (snd v) = []);;


let actuel_danger = danger i j;;
(*if actuel_danger <> [] then begin
    Printf.eprintf "%d %d \n" (fst (List.hd actuel_danger)) (snd (List.hd actuel_danger));
    Printf.eprintf "%f \n" grille_bombes.(fst (List.hd actuel_danger)).(snd (List.hd actuel_danger)).(3)
end;;*)

let choix = ref 0;;
if actuel_danger <> [] then begin
    if  (fst (List.hd actuel_danger)) = i then begin
        if (possible i j 0)&&((danger (i-1) j)=[]) then
            choix := 0
        else begin 
            if (possible i j 2)&&((danger (i+1) j)=[]) then
                choix := 2
            else begin
                if (snd (List.hd actuel_danger)) > j then begin
                    let d_p = danger i (j-1) in
                    if (possible i j 3) then
                        (*if d_p <> [] then begin
                            Printf.eprintf "%d %d \n" (fst (List.hd d_p)) (snd (List.hd d_p));
                            Printf.eprintf "%f \n" grille_bombes.(fst (List.hd d_p)).(snd (List.hd d_p)).(3) end;*)
                        if (d_p=[])||((List.hd d_p)=(List.hd actuel_danger))||(grille_bombes.(fst (List.hd d_p)).(snd (List.hd d_p)).(3)>=grille_bombes.(fst (List.hd actuel_danger)).(snd (List.hd actuel_danger)).(3)) then
                            choix := 3
                        else ()
                    else ()
                end else begin
                    let d_p = danger i (j+1) in
                    if (possible i j 1) then
                        (*if d_p <> [] then begin
                            Printf.eprintf "%d %d \n" (fst (List.hd d_p)) (snd (List.hd d_p));
                            Printf.eprintf "%f \n" grille_bombes.(fst (List.hd d_p)).(snd (List.hd d_p)).(3) end;*)
                        if (d_p=[])||((List.hd d_p)=(List.hd actuel_danger))||(grille_bombes.(fst (List.hd d_p)).(snd (List.hd d_p)).(3)>=grille_bombes.(fst (List.hd actuel_danger)).(snd (List.hd actuel_danger)).(3)) then
                            choix := 1
                        else ()
                    else ()
                end;
            end
        end
    end else begin
        if (possible i j 1)&&((danger i (j+1))=[]) then
            choix := 1
        else begin
            if (possible i j 3)&&((danger i (j-1))=[]) then
                choix := 3
            else begin
                if (fst (List.hd actuel_danger)) > i then begin
                    let d_p = danger (i-1) j in
                    if (possible i j 0) then
                        (*if d_p <> [] then begin
                            Printf.eprintf "%d %d \n" (fst (List.hd d_p)) (snd (List.hd d_p));
                            Printf.eprintf "%f \n" grille_bombes.(fst (List.hd d_p)).(snd (List.hd d_p)).(3) end;*)
                        if (((d_p=[])||((List.hd d_p)=(List.hd actuel_danger)))||(grille_bombes.(fst (List.hd d_p)).(snd (List.hd d_p)).(3)>=grille_bombes.(fst (List.hd actuel_danger)).(snd (List.hd actuel_danger)).(3))) then
                            choix := 0
                        else ()
                    else ()
                end else begin
                    let d_p = danger (i+1) j in
                    if (possible i j 2) then
                        (*if d_p <> [] then begin
                            Printf.eprintf "%d %d \n" (fst (List.hd d_p)) (snd (List.hd d_p));
                            Printf.eprintf "%f \n" grille_bombes.(fst (List.hd d_p)).(snd (List.hd d_p)).(3) end;*)
                        if (((d_p=[])||((List.hd d_p)=(List.hd actuel_danger)))||(grille_bombes.(fst (List.hd d_p)).(snd (List.hd d_p)).(3)>=grille_bombes.(fst (List.hd actuel_danger)).(snd (List.hd actuel_danger)).(3))) then
                            choix := 2
                        else ()
                    else ()
                end
            end
        end
    end
end else begin
    let (obi,obj) = largeur_voisins i j in
    if obi = i && obj = j then begin
        choix := 0;
        while not (possible2 i j !choix) do 
            incr choix
        done;
    end else begin
        if abs (obi-i) > 1 then begin
            if obi > i then begin
                choix := 2;
                if not (possible2 i j 2) then begin
                    if obj > j then begin
                        choix := 1;
                        if not (possible2 i j 1) then begin
                            choix := 0;
                            while not (possible2 i j !choix) do
                                choix := (!choix + 1) mod 5
                            done;
                        end;
                    end else begin
                        choix := 3;
                        if not (possible2 i j 3) then begin
                            choix := 0;
                            while not (possible2 i j !choix) do
                                choix := (!choix + 1) mod 5
                            done;
                        end
                    end
                end
            end else begin
                choix := 0;
                if not (possible2 i j 0) then begin
                    if obj > j then begin
                        choix := 1;
                        if not (possible2 i j 1) then begin
                            choix := 0;
                            while not (possible2 i j !choix) do
                                choix := (!choix + 1) mod 5
                            done;
                        end;
                    end else begin
                        choix := 3;
                        if not (possible2 i j 3) then begin
                            choix := 0;
                            while not (possible2 i j !choix) do
                                choix := (!choix + 1) mod 5
                            done;
                        end
                    end
                end
            end
        end else begin
            if obj > j then begin
                choix := 1;
                if not (possible2 i j 1) then begin
                    if obi > i then begin
                        choix := 2;
                        if not (possible2 i j 2) then begin
                            choix := 0;
                            while not (possible2 i j !choix) do
                                choix := (!choix + 1) mod 5
                            done;
                        end;
                    end else begin
                        choix := 0;
                        if not (possible2 i j 0) then begin
                            choix := 0;
                            while not (possible2 i j !choix) do
                                choix := (!choix + 1) mod 5
                            done;
                        end
                    end
                end
            end else begin
                choix := 3;
                if not (possible2 i j 3) then begin
                    if obi > i then begin
                        choix := 2;
                        if not (possible2 i j 2) then begin
                            choix := 0;
                            while not (possible2 i j !choix) do
                                choix := (!choix + 1) mod 5
                            done;
                        end;
                    end else begin
                        choix := 0;
                        if not (possible2 i j 0) then begin
                            choix := 0;
                            while not (possible2 i j !choix) do
                                choix := (!choix + 1) mod 5
                            done;
                        end
                    end
                end
            end
        end
    end
end;;

let can_escape i1 j1 i2 j2 =
    let q = Queue.create () in
    let visited = Array.make_matrix lignes colonnes false in
    visited.(i1).(j1)<-true;
    let e = ref 0 in
    Queue.push (i2,j2) q;
    while not (Queue.is_empty q)&&(!e<4) do
        let (k,l) = Queue.pop q in
        if (grille.(k).(l) <> 1)&&(grille.(k).(l)<>2)&&(grille_bombes.(k).(l)=[||]) then begin
            incr e;
            visited.(k).(l)<-true;
            let v = voisins k l in
            for n = 0 to 3 do
                if (((fst v.(n))>=0 && (fst v.(n))<lignes && (snd v.(n))>=0 && (snd v.(n))<colonnes))&&(not visited.(fst v.(n)).(snd v.(n))) then
                    Queue.push v.(n) q;
            done
        end;
    done;
    !e;;

let action = ref 0 ;;
let act_v = voisins i j;;
let p_vois = (if !choix = 4 then act_v else (voisins (fst act_v.(!choix)) (snd act_v.(!choix))));;
if joueurs.(player).(6)>0 then action := 2;;
if (Array.fold_left (fun acc (k,l) -> if (valide k l)&&((grille.(k).(l)=2)||((grille.(i).(j) <> player+3)&&(grille.(k).(l)>=3 && grille.(k).(l)<>(3+player))||(grille.(k).(l)=0))) then true else acc) false act_v)&&(!action <> 4)&&((Array.fold_left (fun acc (k,l) -> if (valide k l)&&(grille.(k).(l)<>1)&&(grille.(k).(l)<>2)&&(grille_bombes.(k).(l)=[||])&&(danger_c k l = [])&&((k<>i)||(l<>j))(*&&(joueurs.(player).(5)<=2 ||((k<>i)&&(l<>j)*) then acc+1 else acc) 0 p_vois)>=1)&&(Array.for_all (fun (k,l) -> (valide k l)&&(powerups.(k).(l)= (-1))) act_v) then
    if joueurs.(player).(5)=1 || (let c =can_escape i j (fst act_v.(!choix)) (snd act_v.(!choix)) in c>3 || c>joueurs.(player).(5)) then
        action := 1;;

Printf.printf "%d %d" (!choix) (!action);;





                    




